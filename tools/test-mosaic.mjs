#!/usr/bin/env node
// Behaviour test for assets/mosaic.js, the opening of Smalti's one-sheet: the
// title is restored as a mosaic. It starts as empty slots, and glazed tiles seat
// into them from left to right, as pieces are placed in the game. No
// dependencies, no browser:
//
//     node tools/test-mosaic.mjs
//
// The cells, the plan and the timeline are pure functions, run here in a sandbox
// with no DOM; the drawing itself is checked by eye in a browser.
import fs from 'node:fs';
import vm from 'node:vm';

const sandbox = {};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
for (const f of ['opening.js', 'mosaic.js']) vm.runInContext(fs.readFileSync(new URL(`../assets/${f}`, import.meta.url), 'utf8'), sandbox);
const M = sandbox.NinjaMosaic;

let failed = 0;
function check(name, ok, detail = '') {
  if (!ok) { failed++; console.error(`FAIL ${name}${detail ? ': ' + detail : ''}`); }
}

check('the script loads without a document and exposes its pure parts',
  M && ['cells', 'plan', 'tileState', 'duration'].every((k) => typeof M[k] === 'function'));

// A synthetic mask (alpha per pixel, row by row): a 200x60 field with the left
// half inked and one stray pixel at the right that must not make a tile.
const W = 200, H = 60;
const alpha = new Uint8ClampedArray(W * H);
for (let y = 10; y < 50; y++) for (let x = 0; x < 100; x++) alpha[y * W + x] = 255;
alpha[30 * W + 180] = 255;
const cells = M.cells(alpha, W, H, 10);
check('cells cover the inked area', cells.length >= 30 && cells.length <= 45, `${cells.length}`);
check('cells sit only where the ink is', cells.every((c) => c.x < 105 && c.y > 5 && c.y < 55));
check('cells carry their grid index', cells.every((c) => Number.isInteger(c.i) && Number.isInteger(c.j)));

// A field of cells for the plan: a block 60 wide and 10 tall on a 20px grid,
// with grid indices as M.cells gives them.
const row = [];
for (let i = 0; i < 60; i++) for (let j = 0; j < 10; j++) row.push({ x: 10 + i * 20, y: 10 + j * 20, i, j });
const tiles = M.plan(row, { seed: 7, width: 1200, cell: 20 });
check('every cell gets exactly one tile', tiles.length === row.length
  && new Set(tiles.map((t) => `${t.i},${t.j}`)).size === row.length);

const again = M.plan(row, { seed: 7, width: 1200, cell: 20 });
check('the plan is deterministic', JSON.stringify(again) === JSON.stringify(tiles));

// The cells are cut into the game's pieces: tetrominoes and pentominoes, each
// one connected, one glaze, and seated together.
const pieces = new Map();
for (const t of tiles) { if (!pieces.has(t.piece)) pieces.set(t.piece, []); pieces.get(t.piece).push(t); }
const sizes = [...pieces.values()].map((p) => p.length);
const inGamePieces = sizes.filter((n) => n === 4 || n === 5).reduce((a, n) => a + n, 0) / tiles.length;
check('most cells sit in tetrominoes or pentominoes', inGamePieces >= 0.8, inGamePieces.toFixed(2));
check('no piece is larger than a pentomino', sizes.every((n) => n <= 5), String(Math.max(...sizes)));
check('no piece is a monomino or a domino: the game has none', sizes.every((n) => n >= 3), String(Math.min(...sizes)));
const connected = (p) => {
  const key = (t) => `${t.i},${t.j}`, all = new Set(p.map(key)), seen = new Set([key(p[0])]), todo = [p[0]];
  while (todo.length) {
    const t = todo.pop();
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const k = `${t.i + di},${t.j + dj}`;
      if (all.has(k) && !seen.has(k)) { seen.add(k); todo.push(p.find((x) => key(x) === k)); }
    }
  }
  return seen.size === p.length;
};
check('every piece is one connected shape', [...pieces.values()].every(connected));
check('a piece is one glaze and seats as one', [...pieces.values()].every((p) =>
  p.every((t) => t.color === p[0].color && t.delay === p[0].delay && t.spin === p[0].spin
    && t.px === p[0].px && t.py === p[0].py)));

// A coloured piece is set in ivory: no two coloured pieces share an edge, so
// each one's shape stays readable.
const byCell = new Map(tiles.map((x) => [`${x.i},${x.j}`, x]));
const touching = tiles.filter((x) => x.color !== M.GLAZE.ivory).some((x) =>
  [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([di, dj]) => {
    const n = byCell.get(`${x.i + di},${x.j + dj}`);
    return n && n.piece !== x.piece && n.color !== M.GLAZE.ivory;
  }));
check('no two coloured pieces touch', !touching);

// Every letter carries colour: in a field of separate strokes (thin, like an
// "i", and wide), each stroke of eight cells or more gets a coloured piece.
const strokes = [];
for (let s = 0; s < 8; s++) {
  const w = s % 2 ? 3 : 6;
  for (let i = 0; i < w; i++) for (let j = 0; j < 10; j++) strokes.push({ x: 10 + (s * 10 + i) * 20, y: 10 + j * 20, i: s * 10 + i, j });
}
for (const seed of [1, 2, 3, 7, 11, 42]) {
  const laid = M.plan(strokes, { seed, width: 1600, cell: 20 });
  const bare = [];
  for (let s = 0; s < 8; s++) {
    const own = laid.filter((x) => x.i >= s * 10 && x.i < s * 10 + 10);
    if (!own.some((x) => x.color !== M.GLAZE.ivory)) bare.push(s);
  }
  check(`every stroke has a coloured piece (seed ${seed})`, bare.length === 0, `bare strokes ${bare}`);
  const counts = new Map();
  for (const x of laid) counts.set(x.piece, (counts.get(x.piece) || 0) + 1);
  check(`strokes are cut into pieces of three to five (seed ${seed})`, [...counts.values()].every((n) => n >= 3 && n <= 5),
    [...counts.values()].filter((n) => n < 3 || n > 5).join(','));
  check(`every stroke cell is laid (seed ${seed})`, laid.length === strokes.length);
}

// Ragged letterforms: random blobs, every one cut into pieces of three to five
// with no cell left over, whatever the seed.
for (const seed of [3, 5, 8, 13, 21]) {
  const r = (() => { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  const blob = [];
  for (let i = 0; i < 14; i++) for (let j = 0; j < 9; j++) if (r() > 0.2 || (i % 4 === 0)) blob.push({ x: 10 + i * 20, y: 10 + j * 20, i, j });
  const laid = M.plan(blob, { seed, width: 300, cell: 20 });
  const counts = new Map();
  for (const x of laid) counts.set(x.piece, (counts.get(x.piece) || 0) + 1);
  check(`a ragged shape has no piece under three (seed ${seed})`, [...counts.values()].every((n) => n >= 3 && n <= 5),
    [...counts.values()].filter((n) => n < 3 || n > 5).join(','));
}

// The title reads as glazed white: ivory carries most pieces, the game's
// coloured glazes the rest.
const ivory = tiles.filter((t) => t.color === M.GLAZE.ivory).length / tiles.length;
check('ivory carries the title', ivory >= 0.6 && ivory < 0.9, ivory.toFixed(2));
check('every tile is one of the game glazes', tiles.every((t) => Object.values(M.GLAZE).includes(t.color)));

// Pieces are placed from left to right: the left fifth is seated before the right fifth starts.
const left = tiles.filter((t) => t.x < 240), right = tiles.filter((t) => t.x > 960);
const rightStart = Math.min(...right.map((t) => t.delay));
check('the restoration runs left to right', Math.max(...left.map((t) => t.delay)) < rightStart,
  `left last ${Math.max(...left.map((t) => t.delay))}, right first ${rightStart}`);

// A piece: empty slots before its turn; mid-flight it is lifted, turned and
// larger, never from nothing; at rest it sits square on the grid, as in the game.
const t = tiles[tiles.length - 1];
const before = M.tileState(t, t.delay - 1);
check('before its turn a tile is an empty slot', before.alpha === 0 && before.slot === true);
const mid = M.tileState(t, t.delay + M.TILE_MS / 3);
check('mid-flight it is lifted, turned and enlarged',
  mid.alpha > 0 && mid.scale > 1 && mid.scale < 1.4 && mid.lift > 0 && mid.angle !== 0);
const rest = M.tileState(t, t.delay + M.TILE_MS);
check('at rest it is seated square', rest.alpha === 1 && rest.scale === 1 && rest.lift === 0 && rest.angle === 0);

const end = M.duration(tiles);
check('every tile is seated by the end', tiles.every((x) => M.tileState(x, end).scale === 1));
check('the whole opening stays short', end + M.GLAZE_MS <= 2600, `${end + M.GLAZE_MS}ms`);

// A phone or a home sheet sets the title small: it takes a coarser grid, so a
// tile still reads as a tile (at least 5px), about eleven to a letter's height.
check('a small title takes a coarser grid', M.cellFor(60) >= 5 && Math.abs(M.cellFor(60) - 60 / 11) < 0.01, String(M.cellFor(60)));
check('a poster title keeps the fine grid', Math.abs(M.cellFor(204) - 12) < 0.01, String(M.cellFor(204)));

// The home trailer runs the same plan faster: seated and glazed in 1.7s.
const trailer = M.plan(row, { seed: 7, width: 1200, cell: 20, sweep: 360 });
check('the trailer is short', M.duration(trailer) + M.GLAZE_MS <= 1700, `${M.duration(trailer) + M.GLAZE_MS}ms`);

// The 404: the number is set whole at once, then a few whole pieces work loose
// one after another and fall out, leaving their slots empty.
const broken = M.loosen(tiles, { seed: 3, share: 0.1 });
const loose = new Map();
for (const x of broken) if (x.fall !== undefined) { if (!loose.has(x.piece)) loose.set(x.piece, new Set()); loose.get(x.piece).add(x.fall); }
const pieceCount = new Set(tiles.map((x) => x.piece)).size;
check('the 404 starts whole', broken.every((x) => M.tileState(x, 0).alpha === 1 && !M.tileState(x, 0).slot));
check('about a tenth of its pieces fall', loose.size >= 1 && Math.abs(loose.size - pieceCount * 0.1) <= 1, `${loose.size} of ${pieceCount}`);
check('a piece falls as one', [...loose.values()].every((s) => s.size === 1));
const times = [...loose.values()].map((s) => [...s][0]).sort((a, b) => a - b);
check('they fall one after another', times.every((v, n) => n === 0 || v - times[n - 1] >= 200), times.join(','));
const after = M.duration(broken);
check('a fallen piece leaves an empty slot', broken.filter((x) => x.fall !== undefined).every((x) => M.tileState(x, after).alpha === 0 && M.tileState(x, after).slot));
check('the rest stays set', broken.filter((x) => x.fall === undefined).every((x) => M.tileState(x, after).alpha === 1));
const midFall = broken.find((x) => x.fall !== undefined);
const falling = M.tileState(midFall, midFall.fall + M.FALL_MS / 2);
check('a falling piece drops and turns', falling.drop > 0 && falling.alpha > 0);

if (failed) { console.error(`${failed} failed`); process.exit(1); }
console.log('all passed');
