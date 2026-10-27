#!/usr/bin/env node
// Behaviour test for assets/flecto.js, the opening of FlectoBI's one-sheet: one
// set of points shown as a bar chart, then a bubble map, then a 3D scatter that
// is turned, 15 degrees at a time, until it faces front and reads as the title.
// No dependencies, no browser:
//
//     node tools/test-flecto.mjs
import fs from 'node:fs';
import vm from 'node:vm';

const sandbox = {};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
for (const f of ['opening.js', 'land.js', 'flecto.js']) vm.runInContext(fs.readFileSync(new URL(`../assets/${f}`, import.meta.url), 'utf8'), sandbox);
const F = sandbox.NinjaFlecto;

let failed = 0;
function check(name, ok, detail = '') {
  if (!ok) { failed++; console.error(`FAIL ${name}${detail ? ': ' + detail : ''}`); }
}

check('the script loads without a document and exposes its pure parts',
  F && ['layout', 'camera', 'project', 'at', 'scene', 'colour'].every((k) => typeof F[k] === 'function') && F.END > 0);

// A synthetic title: three letters of unequal weight on a 10px grid, the ink
// box 400 wide from x 100, 100 tall from y 50.
const cell = 10, pts = [];
const blocks = [[100, 140], [220, 260], [300, 500]];
for (const [x0, x1] of blocks) for (let x = x0 + 5; x < x1; x += cell) for (let y = 55; y < 150; y += cell) pts.push({ x, y });
const ink = { left: 100, top: 50, width: 400, height: 100 };
const map = { x: 320, y: 420, w: 500 };
const L = F.layout(pts, { cell, ink, map, seed: 5 });
const near = (a, b, e = 0.01) => Math.abs(a - b) <= e;
const deg = Math.PI / 180;

check('every point has its place in each view', L.points.length === pts.length
  && L.points.every((p) => p.title && p.bar && p.city && Number.isInteger(p.cityIndex)));
check('the layout is deterministic', JSON.stringify(F.layout(pts, { cell, ink, map, seed: 5 })) === JSON.stringify(L));

// The reveal: facing front, the scatter is the title, point for point; turned
// away, its depth scatters the letters.
const end = F.camera(F.END);
check('it ends facing front', end.yaw === 0 && end.pitch === 0);
check('facing front, every point lands on its cell of the title', L.points.every((p, n) => {
  const s = F.project(F.at(p, F.END, L), end, L.centre);
  return near(s.x, pts[n].x) && near(s.y, pts[n].y);
}));
check('the points stand at different depths', new Set(L.points.map((p) => Math.round(p.title.z))).size > pts.length / 4);
const turned = F.camera(F.TURN[0] - 10);
const err = L.points.reduce((a, p, n) => a + Math.abs(F.project(F.at(p, F.TURN[0] - 10, L), turned, L.centre).x - pts[n].x), 0) / pts.length;
check('turned away, the letters are scattered', err > cell * 3, err.toFixed(1));

// The bar chart is the title's own outline: a bar per stretch of the title,
// as tall as the ink in it, all standing on the title's baseline.
const baseline = ink.top + ink.height;
check('bars stand on the baseline', L.bars.every((b) => near(b.base, baseline)));
check('a bar holds the points of its stretch', L.bars.reduce((a, b) => a + b.n, 0) === pts.length);
const tallest = L.bars.reduce((a, b) => (b.n > a.n ? b : a));
check('the tallest bar is where the ink is heaviest', tallest.x > 300, `${tallest.x}`);
check('a bar is as tall as its points stacked', L.bars.every((b) => near(b.top, baseline - Math.ceil(b.n / b.cols) * cell)));
check('every bar point sits inside its bar, on the front plane', L.points.every((p) => {
  const b = L.bars[p.barIndex];
  return p.bar.z === 0 && p.bar.y < baseline && p.bar.y > b.top && Math.abs(p.bar.x - b.x) <= b.w / 2;
}));
const front = F.camera(F.BARS[1]);
check('the bars are seen flat, from the front', front.yaw === 0 && front.pitch === 0);
check('the bars are full when the map begins', L.points.every((p) => {
  const q = F.at(p, F.BARS[1], L);
  return near(q.x, p.bar.x) && near(q.y, p.bar.y);
}));
check('the bars grow from the baseline', L.points.every((p) => F.at(p, 0, L).y >= p.bar.y - 0.01 && near(F.at(p, 0, L).y, baseline, cell)));

// The bubble map: the floor tilts back, a world of dots appears on it, and the
// points gather into bubbles over cities, a bubble's area by its points.
const mapCam = F.camera(F.MAP[1]);
check('the map is seen from above at a slant', near(mapCam.pitch, 55 * deg, 1e-6) && mapCam.yaw === 0);
check('on the map every point lies on the floor', L.points.every((p) => near(F.at(p, F.MAP[1], L).y, L.floorY)));
check('a bubble holds its points', L.points.every((p) => {
  const c = L.cities[p.cityIndex], q = F.at(p, F.MAP[1], L);
  return Math.hypot(q.x - c.x, q.z - c.z) <= c.r + 0.01;
}));
check('a bubble\'s area is by its points', L.cities.filter((c) => c.n).every((c) => near(c.r * c.r / c.n, L.cities.find((d) => d.n).r ** 2 / L.cities.find((d) => d.n).n, 1e-6)));
const centreOf = F.project({ x: map.x, y: L.floorY, z: 0 }, mapCam, L.centre);
check('the map is centred where it was asked', near(centreOf.x, map.x) && near(centreOf.y, map.y), JSON.stringify(centreOf));
const north = F.project(F.geo(0, 50, L), mapCam, L.centre), south = F.project(F.geo(0, -30, L), mapCam, L.centre);
check('north is up on the map', north.y < south.y);
const west = F.geo(-120, 0, L), east = F.geo(120, 0, L);
check('the map spans its width', near(east.x - west.x, map.w * 240 / 360));
check('every city on the map is used', L.cities.every((c) => c.n > 0));

// Turning: as in FlectoBI, a 3D Visual never spins by itself. The camera rises
// into a corner view while the points lift off the map; then it is turned in
// four snaps of 15 degrees, holding still between them.
const yaws = new Set(), still = [];
for (let t = F.TURN[0]; t <= F.END; t += 5) {
  const c = F.camera(t);
  const settled = [0, -15, -30, -45, -60].some((d) => near(c.yaw, d * deg, 1e-9));
  if (settled) yaws.add(Math.round(c.yaw / deg)); else still.push(t);
}
check('it is turned in 15-degree steps', [...yaws].sort((a, b) => a - b).join(',') === '-60,-45,-30,-15,0', [...yaws].join(','));
check('each step is a snap', still.length * 5 <= 4 * 130, `${still.length * 5}ms moving`);
check('it starts its turn from a corner view', near(F.camera(F.TURN[0]).yaw, -60 * deg, 1e-9) && near(F.camera(F.TURN[0]).pitch, 20 * deg, 1e-9));
check('the floor tips no more than straight down at the map', [0, 500, 1200, 1700, 2000, 2600, 3300].every((t) => F.camera(t).pitch <= 55 * deg + 1e-9 && F.camera(t).pitch >= 0));

// What is drawn when.
const s = (t) => F.scene(t);
check('the land shows only for the map', s(F.MAP[1]).land > 0.9 && s(0).land === 0 && s(F.TURN[0]).land === 0);
check('the floor and drop lines show while it is turned away', s(F.TURN[0]).floor > 0.5 && s(F.TURN[0]).drops > 0.5);
check('facing front, the floor and drop lines are gone', s(F.END).floor === 0 && s(F.END).drops === 0);
check('at the end the type takes over from the points', s(F.END).dots === 0 && s(F.END).type === 1 && s(F.TURN[1]).type === 0);
check('the whole opening stays under four seconds', F.END <= 3800, `${F.END}`);

// Colour by height, as the 3D Scatter offers it: the highest points lightest.
check('colour by height', F.colour(L.points.find((p) => p.h > 0.9), F.TURN[0], '#66d4c8', '#ffffff') !== F.colour(L.points.find((p) => p.h < 0.1), F.TURN[0], '#66d4c8', '#ffffff'));
check('the title ends in one colour', new Set(L.points.map((p) => F.colour(p, F.END, '#66d4c8', '#ffffff'))).size === 1);

if (failed) { console.error(`${failed} failed`); process.exit(1); }
console.log('all passed');
