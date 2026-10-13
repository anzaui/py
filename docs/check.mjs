#!/usr/bin/env node
/**
 * docs/check.mjs — browser smoke test for a built static docs site.
 *
 * Serves <site dir> under <base> (the GitHub Pages sub-path), loads the home
 * page and every page linked from the sidebar in headless Chrome, and fails
 * on: JavaScript errors, console errors, failed or 4xx/5xx requests, a loader
 * still visible after load, a page without a heading, no sidebar links, or a
 * sidebar click that doesn't navigate to and render the target page (soft or
 * full page loads both count).
 *
 * Usage:
 *   node docs/check.mjs <site dir> <base> [--links <selector>] [--heading <selector>]
 *   e.g. node docs/check.mjs _site /py
 *
 * Options (or environment variables):
 *   --links    CHECK_LINKS    sidebar link selector   (default: .sidebar-tree a, Furo)
 *   --heading  CHECK_HEADING  page heading selector   (default: h1)
 *
 * Needs: puppeteer-core (PUPPETEER_CORE = path to its ESM entry) and Chrome
 * (CHROME_PATH, default /usr/bin/google-chrome).
 */

import { createServer } from 'node:http';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { extname, join, normalize, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const positional = [];
const options = { links: process.env.CHECK_LINKS || '.sidebar-tree a', heading: process.env.CHECK_HEADING || 'h1' };
for (let args = process.argv.slice(2); args.length; ) {
  const arg = args.shift();
  if (arg === '--links' || arg === '--heading') options[arg.slice(2)] = args.shift();
  else positional.push(arg);
}
const [siteDir = '_site', rawBase = ''] = positional;
const base = rawBase.replace(/\/+$/, '');
const root = resolve(siteDir);

if (!process.env.PUPPETEER_CORE) {
  console.error('docs check: set PUPPETEER_CORE to puppeteer-core/lib/esm/puppeteer/puppeteer-core.js');
  process.exit(2);
}
const puppeteer = (await import(pathToFileURL(process.env.PUPPETEER_CORE).href)).default;
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
  '.json': 'application/json',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.xml': 'application/xml',
  '.txt': 'text/plain',
  '.inv': 'application/octet-stream',
};

// Static server that behaves like GitHub Pages under a sub-path.
const server = createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  if (url.pathname !== base && !url.pathname.startsWith(base + '/')) return res.writeHead(404).end();
  const rel = decodeURIComponent(url.pathname.slice(base.length)) || '/';
  let file = normalize(join(root, rel));
  if (file !== root && !file.startsWith(root + '/')) return res.writeHead(404).end();
  if (existsSync(file) && statSync(file).isDirectory()) {
    if (!url.pathname.endsWith('/')) return res.writeHead(301, { location: url.pathname + '/' }).end();
    file = join(file, 'index.html');
  }
  if (!existsSync(file)) return res.writeHead(404).end();
  res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' }).end(readFileSync(file));
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const origin = `http://127.0.0.1:${server.address().port}`;

const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  args: ['--no-sandbox'],
  defaultViewport: { width: 1280, height: 900 },
});
const problems = [];

/** Same-origin pages under base, without the fragment. */
function internal(href) {
  try {
    const url = new URL(href, origin);
    if (url.origin !== origin || !(url.pathname === base || url.pathname.startsWith(base + '/'))) return null;
    return url.pathname + url.search;
  } catch {
    return null;
  }
}

function watch(page, issues) {
  page.on('pageerror', (e) => issues.push(`JS error: ${e.message}`));
  page.on('console', (m) => m.type() === 'error' && issues.push(`console error: ${m.text()}`));
  page.on('requestfailed', (r) => issues.push(`request failed: ${r.url()} (${r.failure()?.errorText})`));
  page.on('response', (r) => r.status() >= 400 && issues.push(`HTTP ${r.status()}: ${r.url()}`));
}

async function inspect(page) {
  return page.evaluate(
    ({ links, heading }) => {
      const visible = (el) => {
        const s = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && r.width > 0 && r.height > 0;
      };
      return {
        heading: document.querySelector(heading)?.textContent?.trim(),
        loaders: [...document.querySelectorAll('[class*="loading" i],[aria-busy="true"],ui-spinner')].filter(visible).length,
        links: [...document.querySelectorAll(links)].map((a) => a.href),
      };
    },
    options,
  );
}

async function visit(path) {
  const page = await browser.newPage();
  const issues = [];
  watch(page, issues);
  await page.goto(origin + path, { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise((r) => setTimeout(r, 300));
  const state = await inspect(page);
  if (!state.heading) issues.push(`no ${options.heading} rendered`);
  if (state.loaders) issues.push(`${state.loaders} loader(s) still visible`);
  return { page, issues, state };
}

const home = base + '/';
const first = await visit(home);
const links = [...new Set(first.state.links.map(internal).filter(Boolean))];
if (!links.length) first.issues.push(`no sidebar links (${options.links})`);
problems.push(...first.issues.map((i) => `${home}: ${i}`));

// Navigation: click a sidebar entry that is not the current page.
const target = links.find((href) => href !== home && href !== base + '/index.html');
if (target) {
  const before = first.state.heading;
  const handles = await first.page.$$(options.links);
  let clicked = false;
  for (const handle of handles) {
    const href = internal(await handle.evaluate((a) => a.href));
    if (href !== target) continue;
    await Promise.all([
      first.page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 }).catch(() => null),
      handle.click(),
    ]);
    clicked = true;
    break;
  }
  await new Promise((r) => setTimeout(r, 500));
  const after = await first.page.evaluate((h) => document.querySelector(h)?.textContent?.trim(), options.heading);
  const at = internal(first.page.url());
  if (!clicked) problems.push(`navigation: could not click the sidebar link to ${target}`);
  else if (at !== target) problems.push(`navigation: clicking ${target} ended at ${at}`);
  else if (!after || after === before) problems.push(`navigation: ${target} did not render a new page`);
}
await first.page.close();

// Load every page in the sidebar.
for (const href of links) {
  const { page, issues } = await visit(href);
  problems.push(...issues.map((i) => `${href}: ${i}`));
  await page.close();
}

await browser.close();
server.close();
if (problems.length) {
  console.error(`docs check: ${problems.length} problem(s)\n` + problems.map((p) => '  ' + p).join('\n'));
  process.exit(1);
}
console.log(`docs check: ok (${links.length + 1} pages, navigation to ${target} works)`);
