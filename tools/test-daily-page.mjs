#!/usr/bin/env node
// Behaviour test for the one inline script on games/smalti/daily/index.html, the
// reader of the share link's ?d=YYYY-MM-DD. No dependencies, no browser:
//
//     node tools/test-daily-page.mjs
//
// The script is lifted out of the page and run in a sandbox with a fake DOM, a
// fixed "now" and a chosen locale and time zone, so the cases are exact.
// check-site.py cannot do this: it only reads the page, it cannot run it.
import fs from 'node:fs';
import vm from 'node:vm';

const PAGE = new URL('../games/smalti/daily/index.html', import.meta.url);
const html = fs.readFileSync(PAGE, 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
  .map((m) => m[1])
  .filter((s) => !s.includes('ninjaapps-theme'));   // the shared theme snippet is not ours to test
if (scripts.length !== 1) {
  console.error(`expected exactly one page script, found ${scripts.length}`);
  process.exit(1);
}
const DEFAULT = (html.match(/id="daily-line">([^<]*)</) || [])[1];

function node(tag) {
  return {
    tagName: tag, children: [], _text: '', dateTime: undefined,
    get textContent() { return this._text; },
    set textContent(v) { this._text = String(v); this.children = []; },
    appendChild(c) { this.children.push(c); return c; },
  };
}
const render = (n) => n._text + n.children.map((c) => c._text).join('');

/** Run the page script. `utcOffsetHours` is the visitor's clock: the local
 *  getters report wall-clock time at that offset, as a real device would. */
function run({ search, now = '2026-10-13T12:00:00Z', locale = 'en-US', utcOffsetHours = 0, hasLine = true }) {
  const line = node('h2');
  line._text = DEFAULT;
  const NOW = Date.parse(now);
  const shifted = (d) => new Date(d.getTime() + utcOffsetHours * 3600e3);
  class FakeDate extends Date {
    constructor(...a) { if (a.length === 0) super(NOW); else super(...a); }
    getFullYear() { return shifted(this).getUTCFullYear(); }
    getMonth() { return shifted(this).getUTCMonth(); }
    getDate() { return shifted(this).getUTCDate(); }
  }
  const formatted = [];
  const FakeIntl = {
    DateTimeFormat: class {
      constructor(l, o) {
        formatted.push(o);
        this.f = new Intl.DateTimeFormat(l === undefined ? locale : l, o);
      }
      format(d) { return this.f.format(d); }
    },
  };
  const sandbox = {
    location: { search }, URLSearchParams, Date: FakeDate, Intl: FakeIntl,
    document: {
      getElementById: (id) => (hasLine && id === 'daily-line' ? line : null),
      createElement: (t) => node(t),
    },
  };
  vm.runInNewContext(scripts[0], sandbox);
  return { text: render(line), line, formatted };
}

let failed = 0;
function expect(name, got, want) {
  const ok = got === want;
  if (!ok) failed++;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}${ok ? '' : `\n       got:  ${JSON.stringify(got)}\n       want: ${JSON.stringify(want)}`}`);
}
const SAYS = 'I restored the mosaic for ';

// The happy path, in the visitor's locale. The day itself never moves.
const day = { 'en-US': 'October 13, 2026', 'en-GB': '13 October 2026', de: '13. Oktober 2026',
  fr: '13 octobre 2026', ja: '2026年10月13日', tr: '13 Ekim 2026' };
for (const [loc, label] of Object.entries(day)) {
  expect(`valid day in ${loc}`, run({ search: '?d=2026-10-13', locale: loc }).text, SAYS + label);
}
for (const off of [-11, -5, 0, 2, 5.5, 14]) {
  expect(`the day does not shift for a visitor at UTC${off >= 0 ? '+' : ''}${off}`,
    run({ search: '?d=2026-10-13', utcOffsetHours: off }).text, SAYS + 'October 13, 2026');
}
{
  const r = run({ search: '?d=2026-10-13' });
  expect('<time datetime> carries the validated key', r.line.children[0] && r.line.children[0].dateTime, '2026-10-13');
  expect('only a <time> element is ever added', r.line.children.map((c) => c.tagName).join(','), 'time');
  expect('the date is formatted in UTC, whatever the visitor\'s zone', r.formatted[0] && r.formatted[0].timeZone, 'UTC');
}
expect('extra params are ignored', run({ search: '?utm_source=x&d=2026-10-13&fbclid=1' }).text, SAYS + 'October 13, 2026');
expect('param order does not matter', run({ search: '?x=1&d=2026-10-13' }).text, SAYS + 'October 13, 2026');

// Bounds: the first daily (2026-07-01) up to two days after the visitor's own date.
expect('first daily is valid', run({ search: '?d=2026-07-01' }).text, SAYS + 'July 1, 2026');
expect('the day before the first daily falls back', run({ search: '?d=2026-06-30' }).text, DEFAULT);
expect('visitor\'s date +2 is valid', run({ search: '?d=2026-10-15' }).text, SAYS + 'October 15, 2026');
expect('visitor\'s date +3 falls back', run({ search: '?d=2026-10-16' }).text, DEFAULT);
expect('yesterday is valid', run({ search: '?d=2026-10-12' }).text, SAYS + 'October 12, 2026');
// Time zones span 26 hours: a sharer at UTC+14 can be a day ahead of a visitor at UTC-11.
expect('a sharer a day ahead of a UTC-11 visitor still reads',
  run({ search: '?d=2026-10-14', utcOffsetHours: -11 }).text, SAYS + 'October 14, 2026');
expect('the bound follows the visitor\'s date (UTC+14 is a day later)',
  run({ search: '?d=2026-10-16', utcOffsetHours: 14 }).text, SAYS + 'October 16, 2026');
expect('...and does not leak to a UTC-11 visitor',
  run({ search: '?d=2026-10-16', utcOffsetHours: -11 }).text, DEFAULT);

// Strict calendar validation.
for (const bad of ['2026-02-30', '2026-02-29', '2026-13-01', '2026-00-10', '2026-10-32', '2026-10-00',
  '2026-04-31', '2026-11-31']) {
  expect(`impossible date ${bad} falls back`, run({ search: `?d=${bad}`, now: '2026-12-01T00:00:00Z' }).text, DEFAULT);
}
expect('29 February is real in a leap year', run({ search: '?d=2028-02-29', now: '2028-03-01T00:00:00Z' }).text, SAYS + 'February 29, 2028');
expect('29 February is not real otherwise', run({ search: '?d=2027-02-29', now: '2028-03-01T00:00:00Z' }).text, DEFAULT);

// Malformed input of every flavour falls back, and never throws.
const garbage = ['', '?', '?d=', '?d=abc', '?d=2026-1-5', '?d=26-10-13', '?d=20261013', '?d=2026/10/13',
  '?d=2026-10-13T00:00', '?d=2026-10-13Z', '?d=%202026-10-13', '?d=2026-10-13%20', '?d=2026-10-13%0A',
  '?D=2026-10-13', '?d[]=2026-10-13', '?dd=2026-10-13', '?d=2026-10-13&d=2026-10-12',
  '?d=2026-10-13&d=2026-10-13', '?d=２０２６-１０-１３', '?d=0050-10-13', '?d=-2026-10-13',
  '?d=<img src=x onerror=alert(1)>', '?d=%3Cscript%3Ealert(1)%3C/script%3E', '?d=2026-10-13%23x'];
for (const g of garbage) {
  let out;
  try { out = run({ search: g }).text; } catch (e) { out = `THREW ${e.message}`; }
  expect(`garbage ${JSON.stringify(g)} falls back`, out, DEFAULT);
}

// Degraded environments: nothing throws, the page still reads.
expect('no #daily-line element: silent no-op', run({ search: '?d=2026-10-13', hasLine: false }).text, DEFAULT);

console.log(failed ? `\n${failed} FAILED` : '\nall passed');
process.exit(failed ? 1 : 0);
