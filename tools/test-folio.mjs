#!/usr/bin/env node
// Behaviour test for assets/folio.js, the opening of Dayfolio's one-sheet: the
// title is written a line a day. Each ruled line of the name is inked from
// left to right, one working day after another, dated in the margin, the last
// line today; then the lines close up into solid type. No dependencies:
//
//     node tools/test-folio.mjs
import fs from 'node:fs';
import vm from 'node:vm';

const sandbox = {};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
for (const f of ['opening.js', 'folio.js']) vm.runInContext(fs.readFileSync(new URL(`../assets/${f}`, import.meta.url), 'utf8'), sandbox);
const D = sandbox.NinjaFolio;

let failed = 0;
function check(name, ok, detail = '') {
  if (!ok) { failed++; console.error(`FAIL ${name}${detail ? ': ' + detail : ''}`); }
}

check('the script loads without a document and exposes its pure parts',
  D && ['lines', 'days', 'pen', 'startOf', 'state'].every((k) => typeof D[k] === 'function') && D.END > 0);

// A mask 300x100: two letters, one a block (x 20..120, y 10..90), one a ring
// (x 160..280, y 10..90, hollow from x 190..250, y 30..70).
const W = 300, H = 100, alpha = new Uint8ClampedArray(W * H);
for (let y = 10; y < 90; y++) for (let x = 20; x < 120; x++) alpha[y * W + x] = 255;
for (let y = 10; y < 90; y++) for (let x = 160; x < 280; x++) if (!(x >= 190 && x < 250 && y >= 30 && y < 70)) alpha[y * W + x] = 255;
const L = D.lines(alpha, W, H, 10);

check('the name is cut into ruled lines, a line per row of the grid', L.length === 8, `${L.length}`);
check('lines are in order from top to bottom', L.every((l, n) => n === 0 || l.y > L[n - 1].y));
check('a line is the runs of ink on its row', L[0].runs.length === 2 && L[0].runs[0][0] === 20 && L[0].runs[0][1] === 120);
const hollow = L.find((l) => l.y > 40 && l.y < 60);
check('a line skips the paper inside a letter', hollow.runs.length === 3, JSON.stringify(hollow.runs));
check('every line starts where its ink starts', L.every((l) => l.from === l.runs[0][0] && l.to === l.runs[l.runs.length - 1][1]));

// A line a working day: the dates run back from today, Monday to Friday only,
// the last line dated today (or the Friday before, at a weekend).
const wed = new Date(2026, 9, 28);   // Wednesday 28 October 2026
const days = D.days(8, wed);
check('a date for every line', days.length === 8);
check('the last line is today', days[7] === 'Wed 28', days.join(' '));
check('working days only, in order', days.join(' ') === 'Mon 19 Tue 20 Wed 21 Thu 22 Fri 23 Mon 26 Tue 27 Wed 28', days.join(' '));
check('on a Sunday the last line is Friday', D.days(2, new Date(2026, 10, 1)).join(' ') === 'Thu 29 Fri 30');

// The pen: each line starts after the one above and is written left to right;
// a line is written in no more time than the whole allows.
const first = L[0], last = L[L.length - 1];
check('a line is unwritten before its turn', D.pen(last, L.length - 1, L.length, 0) === null);
check('a line starts when the one above is written', L.every((l, n) => n === 0
  || Math.abs(D.pen(L[n - 1], n - 1, L.length, D.startOf(n, L.length)) - L[n - 1].to) < 0.01));
check('every line is written in full by the end of writing', L.every((l, n) => Math.abs(D.pen(l, n, L.length, D.WRITE[1]) - l.to) < 0.01));
const mid = D.pen(first, 0, L.length, D.WRITE[0] + 60);
check('the pen moves left to right', mid > first.from && mid < first.to, `${mid}`);

// The page: thin ruled strokes while writing, closing into solid type at the
// end; the date shows while the lines are written, and the type takes over.
const s0 = D.state(D.WRITE[0] + 10), s1 = D.state(D.WRITE[1]), sEnd = D.state(D.END);
check('the strokes are thin while written', s0.weight > 0.2 && s0.weight < 0.6, `${s0.weight}`);
check('the strokes close up into solid type', sEnd.weight === 1);
check('the date shows while writing and then goes', s0.date === 1 && sEnd.date === 0);
check('at the end the type takes over', sEnd.type === 1 && sEnd.lines === 0 && s1.type === 0);
check('the whole opening stays short', D.END <= 2800, `${D.END}`);

if (failed) { console.error(`${failed} failed`); process.exit(1); }
console.log('all passed');
