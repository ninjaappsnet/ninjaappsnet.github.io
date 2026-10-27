// FlectoBI's opening: one set of data shown three ways, then turned until it
// reads. The points of the title (one per cell of its letters) are first a bar
// chart standing on the title's baseline, each bar as tall as the ink in its
// stretch of the name; the floor tilts back and they gather into bubbles over
// cities on a map of dots; they lift off the map into a 3D scatter, seen from
// a corner, coloured by height. Then, as in FlectoBI, the view is turned in
// snaps of 15 degrees, never spun, until it faces front. The view is flat (no
// perspective, as FlectoBI draws its 3D Visuals), so facing front the depth
// disappears and the points line up into the name. The type takes over.
//
// The real <h1> stays in the page and ends visible. A click, key, scroll or
// touch ends the opening at once; under reduced motion there is none. The
// layout, camera and timeline are pure, tested by tools/test-flecto.mjs.
// Needs assets/opening.js and assets/land.js.
(function (root) {
  'use strict';
  var O = root.NinjaOpening;
  var deg = Math.PI / 180;

  // The timeline, in ms.
  var BARS = [0, 800];       // the bars grow
  var MAP = [800, 1700];     // the floor tilts back; bubbles gather on the map
  var LIFT = [1700, 2400];   // into a 3D scatter, seen from a corner
  var TURN = [2500, 3400];   // four snaps of 15 degrees to the front
  var HAND = [3400, 3700];   // the type takes over
  var END = HAND[1];
  var MAP_PITCH = 55 * deg, CORNER_YAW = -60 * deg, CORNER_PITCH = 20 * deg;
  var SNAP_MS = 110, SNAPS = [2500, 2730, 2960, 3190];
  var LAT_MID = 8.75;
  var MAP_DOT = 0.55;        // a point's size on the map, against its size in the title        // the middle of the land's rows (75N to 57.5S)

  // Cities and a weight each: where a bubble map of sales would put them.
  var CITIES = [
    [-118.2, 34.0, 6], [-99.1, 19.4, 4], [-87.6, 41.9, 4], [-79.4, 43.7, 3], [-74.0, 40.7, 9],
    [-74.1, 4.7, 2], [-58.4, -34.6, 3], [-46.6, -23.5, 5], [-3.7, 40.4, 3], [-0.1, 51.5, 7],
    [2.35, 48.9, 5], [3.4, 6.5, 3], [13.4, 52.5, 4], [28.0, -26.2, 3], [29.0, 41.0, 4],
    [31.2, 30.0, 3], [36.8, -1.3, 2], [55.3, 25.2, 3], [72.9, 19.1, 6], [77.2, 28.6, 5],
    [103.8, 1.35, 4], [106.8, -6.2, 3], [116.4, 39.9, 5], [121.5, 31.2, 7], [127.0, 37.6, 4],
    [139.7, 35.7, 8], [151.2, -33.9, 4],
  ];

  var span = O.span, easeOut = O.easeOut, easeInOut = O.easeInOut;
  function lerp(a, b, k) { return a + (b - a) * k; }
  function round(v) { return Math.round(v * 1000) / 1000; }

  // A place on the map, on the floor: equirectangular, centred on map.x and
  // the middle of the land, north away from the viewer.
  function geo(lon, lat, L) {
    return { x: L.map.x + lon / 360 * L.map.w, y: L.floorY, z: -(lat - LAT_MID) / 360 * L.map.w };
  }

  function layout(list, o) {
    var rand = O.rng(o.seed || 5), cell = o.cell, ink = o.ink;
    var centre = { x: ink.left + ink.width / 2, y: ink.top + ink.height / 2 };
    var base = ink.top + ink.height, depth = ink.width * 0.3;
    // The floor sits where, tilted back for the map, its middle shows at map.y.
    var floorY = centre.y + (o.map.y - centre.y) / Math.cos(MAP_PITCH);
    var L = { centre: centre, floorY: floorY, map: o.map, cell: cell, depth: depth, base: base, bars: [], cities: [], points: [] };

    // The title, as a scatter: each point keeps its x and height and takes a depth.
    var pts = list.map(function (c) {
      return { title: { x: c.x, y: c.y, z: round((rand() - 0.5) * 2 * depth) },
               h: round(Math.min(1, Math.max(0, (base - c.y) / ink.height))), lift: rand() };
    });

    // The bars: the title cut into stretches, a bar per stretch, as tall as
    // its points stacked. Too tall a bar takes more columns.
    var B = Math.max(6, Math.min(18, Math.round(ink.width / (cell * 5)))), binW = ink.width / B, bins = [];
    for (var b = 0; b < B; b++) bins.push([]);
    pts.forEach(function (p) {
      bins[Math.min(B - 1, Math.max(0, Math.floor((p.title.x - ink.left) / binW)))].push(p);
    });
    var most = 0;
    for (b = 0; b < B; b++) most = Math.max(most, bins[b].length);
    var cols = Math.max(1, Math.floor(binW * 0.72 / cell));
    var tallest = Math.floor(ink.height * 1.4 / cell);
    if (Math.ceil(most / cols) > tallest) cols = Math.min(Math.max(1, Math.floor(binW * 0.95 / cell)), Math.ceil(most / tallest));
    var order = [];
    for (b = 0; b < B; b++) {
      var x = ink.left + (b + 0.5) * binW, w = cols * cell, n = bins[b].length;
      L.bars.push({ x: round(x), w: w, n: n, cols: cols, base: base, top: base - Math.ceil(n / cols) * cell,
                    delay: round(40 + (B > 1 ? b / (B - 1) : 0) * 220) });
      bins[b].sort(function (p, q) { return q.title.y - p.title.y || p.title.x - q.title.x; });
      bins[b].forEach(function (p, idx) {
        p.barIndex = b;
        p.bar = { x: round(x - w / 2 + (idx % cols + 0.5) * cell), y: round(base - (Math.floor(idx / cols) + 0.5) * cell), z: 0 };
        order.push(p);
      });
    }

    // The map: points, from left to right, go to the cities from west to east,
    // as many to each as its weight; a bubble's area is by its points.
    var total = 0, N = order.length;
    CITIES.forEach(function (c) { total += c[2]; });
    var counts = CITIES.map(function (c) { return Math.max(1, Math.floor(c[2] / total * N)); });
    var left = N - counts.reduce(function (a, v) { return a + v; }, 0);
    for (var r = 0; left > 0; r = (r + 1) % CITIES.length, left--) counts[r]++;
    for (r = CITIES.length - 1; left < 0 && r >= 0; r = r > 0 ? r - 1 : CITIES.length - 1) if (counts[r] > 1) { counts[r]--; left++; }
    // On the map a point is drawn smaller (MAP_DOT), so bubbles pack tighter.
    var gap = cell * 0.56 * MAP_DOT, at = 0;
    CITIES.forEach(function (c, ci) {
      var g = geo(c[0], c[1], L), n2 = counts[ci];
      L.cities.push({ x: round(g.x), z: round(g.z), n: n2, r: gap * Math.sqrt(n2) });
      for (var k = 0; k < n2; k++) {
        var p = order[at++], rr = gap * Math.sqrt(k + 0.5), a = k * 2.39996;
        p.cityIndex = ci;
        p.city = { x: round(g.x + rr * Math.cos(a)), y: floorY, z: round(g.z + rr * Math.sin(a)) };
        p.order = round(at / N);
      }
    });
    L.points = pts;
    return L;
  }

  // Where a point is at a time: growing with its bar, travelling to its city,
  // lifting into the scatter.
  function at(p, t, L) {
    if (t < MAP[0]) {
      var bar = L ? L.bars[p.barIndex] : null, g = easeOut(span(t, bar ? bar.delay : 0, 520));
      var base = bar ? bar.base : p.bar.y;
      return { x: p.bar.x, y: base + (p.bar.y - base) * g, z: 0, s: 1 };
    }
    if (t < LIFT[0]) {
      var m = easeInOut(span(t, MAP[0] + p.order * 250, 600));
      return { x: lerp(p.bar.x, p.city.x, m), y: lerp(p.bar.y, p.city.y, m), z: lerp(0, p.city.z, m), s: lerp(1, MAP_DOT, m) };
    }
    var l = easeInOut(span(t, LIFT[0] + p.lift * 150, 550));
    return { x: lerp(p.city.x, p.title.x, l), y: lerp(p.city.y, p.title.y, l), z: lerp(p.city.z, p.title.z, l), s: lerp(MAP_DOT, 1, l) };
  }

  function camera(t) {
    if (t < LIFT[0]) return { yaw: 0, pitch: MAP_PITCH * easeInOut(span(t, MAP[0] + 20, 550)) };
    if (t < TURN[0]) {
      var k = easeInOut(span(t, LIFT[0], LIFT[1] - LIFT[0]));
      return { yaw: CORNER_YAW * k, pitch: lerp(MAP_PITCH, CORNER_PITCH, k) };
    }
    var steps = 0;
    for (var i = 0; i < SNAPS.length; i++) steps += easeOut(span(t, SNAPS[i], SNAP_MS));
    var yaw = CORNER_YAW + 15 * deg * steps, pitch = CORNER_PITCH - 5 * deg * steps;
    if (steps === SNAPS.length) { yaw = 0; pitch = 0; }
    return { yaw: yaw, pitch: pitch };
  }

  // Flat projection: turn about the vertical through the title's centre, then
  // tilt. `d` grows toward the viewer, for drawing back to front.
  function project(p, cam, c) {
    var x = p.x - c.x, y = p.y - c.y, z = p.z;
    var cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw), cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
    var x1 = x * cy + z * sy, z1 = -x * sy + z * cy;
    return { x: c.x + x1, y: c.y + y * cp + z1 * sp, d: z1 * cp - y * sp };
  }

  function scene(t) {
    var turned = Math.min(1, camera(t).pitch / CORNER_PITCH);
    return {
      axis: span(t, 0, 200) * (1 - span(t, 800, 200)),
      land: span(t, 950, 400) * (1 - span(t, 1700, 250)),
      bubbles: span(t, 1150, 250) * (1 - span(t, 1700, 200)),
      floor: span(t, 1900, 400) * turned,
      drops: span(t, 2100, 300) * turned,
      dots: 1 - span(t, HAND[0], HAND[1] - HAND[0]),
      type: span(t, HAND[0], HAND[1] - HAND[0]),
    };
  }

  function hex(c) { return [1, 3, 5].map(function (i) { return parseInt(c.substr(i, 2), 16); }); }
  // Colour by height, as the 3D Scatter offers it, from the app's highlight
  // (low) to white (high); every point ends white, as the type is.
  function colour(p, t, hi, on) {
    var a = span(t, 1800, 400), b = span(t, 3200, 200), w = (1 - b) * a * p.h + b, h = hex(hi), o = hex(on);
    return '#' + [0, 1, 2].map(function (i) { return ('0' + Math.round(lerp(h[i], o[i], w)).toString(16)).slice(-2); }).join('');
  }

  root.NinjaFlecto = {
    layout: layout, at: function (p, t, L) { return at(p, t, L); }, camera: camera, project: project, scene: scene,
    colour: colour, geo: geo, BARS: BARS, MAP: MAP, LIFT: LIFT, TURN: TURN, HAND: HAND, END: END,
  };

  // ----- in the page -----
  if (typeof document === 'undefined') return;

  function sphere(radius, dpr) {
    var s = Math.ceil(radius * 2 * dpr) + 2, c = document.createElement('canvas');
    c.width = c.height = s;
    var g = c.getContext('2d'), m = s / 2;
    var shade = g.createRadialGradient(m - s * 0.15, m - s * 0.18, s * 0.05, m, m, s / 2);
    shade.addColorStop(0, 'rgba(255,255,255,.55)'); shade.addColorStop(0.45, 'rgba(255,255,255,0)');
    shade.addColorStop(1, 'rgba(0,0,0,.28)');
    g.fillStyle = shade; g.beginPath(); g.arc(m, m, s / 2 - 1, 0, Math.PI * 2); g.fill();
    return c;
  }

  function start(host, trailer) {
    var el = trailer ? host.querySelector('.sheet-title a') : host.querySelector('h1');
    if (!el || !O.textOf(el)) return;
    function release() { host.classList.add('opened'); }
    if (O.still()) { release(); return; }
    var st = O.stage(host), ctx = st.ctx, canvas = st.canvas;
    if (!trailer) canvas.style.zIndex = '2';   // over the key art, which the map covers
    var css = getComputedStyle(host);
    var ground = css.getPropertyValue('--app-ground').trim() || '#06454c';
    var hi = css.getPropertyValue('--app-hi').trim() || '#66d4c8';
    var on = css.getPropertyValue('--app-on').trim() || '#ffffff';
    var L, land = [], radius = 4, ball, frame = 0, t0 = trailer ? LIFT[1] : 0, done = false, art = null;

    function measure() {
      st.fit();
      var mk = O.mask(host, el, 0.03);
      if (!mk) return false;
      // About 800 points on a wide screen and 320 on a phone: the grid that
      // gives that many cells of the name.
      var want = trailer ? 260 : st.w > 700 ? 800 : 320, cell = mk.size / 12, list = O.cells(mk.alpha, mk.w, mk.h, cell);
      for (var i = 0; i < 3 && list.length; i++) {
        cell *= Math.sqrt(list.length / want);
        list = O.cells(mk.alpha, mk.w, mk.h, cell);
      }
      if (list.length < 40) return false;
      // The map takes the key art's place: centred on it, as wide as it.
      var hb = host.getBoundingClientRect(), map;
      var shot = !trailer && host.querySelector('.onesheet-art :is(img, video)');
      if (shot) {
        var r = shot.getBoundingClientRect();
        art = { x: r.left - hb.left, y: r.top - hb.top, w: r.width, h: r.height };
        // The map takes the key art's column, below the name.
        var col = host.querySelector('.onesheet-art').getBoundingClientRect();
        map = { x: col.left - hb.left + col.width / 2, y: art.y + Math.min(art.h, st.h - art.y) / 2, w: col.width * 0.98 };
      } else {
        // A home sheet shows only the turn: its floor sits just under the name.
        var cyy = mk.ink.top + mk.ink.height / 2;
        map = { x: mk.ink.left + mk.ink.width / 2, y: cyy + mk.ink.height * 0.9 * Math.cos(MAP_PITCH), w: mk.ink.width };
      }
      L = layout(list, { cell: cell, ink: mk.ink, map: map, seed: 5 });
      radius = cell * 0.42;
      ball = sphere(radius, st.dpr);
      land = [];
      var N = root.NinjaLand;
      if (N && !trailer) {
        N.rows.forEach(function (row, ri) {
          var bits = BigInt('0x' + row).toString(2).padStart(N.cols, '0');
          for (var ci = 0; ci < N.cols; ci++) if (bits[ci] === '1') land.push(geo(-180 + (ci + 0.5) * N.step, N.north - (ri + 0.5) * N.step, L));
        });
      }
      return true;
    }

    function rgba(c, a) { var h = hex(c); return 'rgba(' + h[0] + ',' + h[1] + ',' + h[2] + ',' + a + ')'; }

    function draw(t) {
      var cam = camera(t), sc = scene(t), c = L.centre, i, q;
      var lead = trailer ? span(t, t0, 150) : 1;   // a home sheet's scatter fades in
      st.clear();
      // The map covers the key art while the art's place is the stage.
      if (art) {
        var cover = 1 - span(t, HAND[0], HAND[1] - HAND[0]);
        if (cover > 0) { ctx.fillStyle = rgba(ground, cover); ctx.fillRect(art.x - 40, art.y - 40, art.w + 80, st.h - art.y + 40); }
      }
      if (sc.axis > 0) {
        ctx.strokeStyle = rgba(on, 0.5 * sc.axis); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(L.bars[0].x - L.bars[0].w, L.base + 0.5); ctx.lineTo(L.bars[L.bars.length - 1].x + L.bars[0].w, L.base + 0.5); ctx.stroke();
      }
      if (sc.land > 0) {
        ctx.fillStyle = rgba(on, 0.3 * sc.land);
        var dot = Math.max(1.5, L.map.w / 144 * 0.42);
        for (i = 0; i < land.length; i++) { q = project(land[i], cam, c); ctx.fillRect(q.x - dot / 2, q.y - dot / 2, dot, dot); }
      }
      if (sc.bubbles > 0) {
        for (i = 0; i < L.cities.length; i++) {
          var city = L.cities[i];
          q = project({ x: city.x, y: L.floorY, z: city.z }, cam, c);
          ctx.beginPath(); ctx.ellipse(q.x, q.y, city.r + radius * MAP_DOT, (city.r + radius * MAP_DOT) * Math.sin(cam.pitch) + 0.01, 0, 0, Math.PI * 2);
          ctx.fillStyle = rgba(hi, 0.16 * sc.bubbles); ctx.fill();
          ctx.strokeStyle = rgba(hi, 0.55 * sc.bubbles); ctx.lineWidth = 1; ctx.stroke();
        }
      }
      if (sc.floor > 0) {
        ctx.strokeStyle = rgba(on, 0.16 * sc.floor * lead); ctx.lineWidth = 1;
        var hw = L.depth * 2, hd = L.depth * 1.1;
        ctx.beginPath();
        for (i = 0; i <= 8; i++) {
          var fx = c.x - hw + i * hw / 4, a1 = project({ x: fx, y: L.floorY, z: -hd }, cam, c), b1 = project({ x: fx, y: L.floorY, z: hd }, cam, c);
          ctx.moveTo(a1.x, a1.y); ctx.lineTo(b1.x, b1.y);
        }
        for (i = 0; i <= 4; i++) {
          var fz = -hd + i * hd / 2, a2 = project({ x: c.x - hw, y: L.floorY, z: fz }, cam, c), b2 = project({ x: c.x + hw, y: L.floorY, z: fz }, cam, c);
          ctx.moveTo(a2.x, a2.y); ctx.lineTo(b2.x, b2.y);
        }
        ctx.stroke();
      }
      var drawn = [];
      for (i = 0; i < L.points.length; i++) {
        var p = L.points[i], pos = at(p, t, L), s = project(pos, cam, c);
        s.p = p; s.pos = pos; drawn.push(s);
      }
      drawn.sort(function (a, b) { return a.d - b.d; });
      if (sc.drops > 0) {
        ctx.strokeStyle = rgba(on, 0.14 * sc.drops * lead); ctx.lineWidth = 1;
        ctx.beginPath();
        for (i = 0; i < drawn.length; i++) {
          var f = project({ x: drawn[i].pos.x, y: L.floorY, z: drawn[i].pos.z }, cam, c);
          ctx.moveTo(drawn[i].x, drawn[i].y); ctx.lineTo(f.x, f.y);
        }
        ctx.stroke();
      }
      ctx.globalAlpha = sc.dots * lead;
      var size = ball.width / st.dpr;
      for (i = 0; i < drawn.length; i++) {
        ctx.fillStyle = colour(drawn[i].p, t, hi, on);
        var k = drawn[i].pos.s;
        ctx.beginPath(); ctx.arc(drawn[i].x, drawn[i].y, radius * k, 0, Math.PI * 2); ctx.fill();
        ctx.drawImage(ball, drawn[i].x - size * k / 2, drawn[i].y - size * k / 2, size * k, size * k);
      }
      ctx.globalAlpha = 1;
    }

    // The type comes back, the canvas goes: at the end, or at once on a skip.
    function finish(ms) {
      if (done) return;
      done = true;
      cancelAnimationFrame(frame);
      O.showType(el, ms);
      canvas.style.transition = 'opacity ' + ms + 'ms ease';
      canvas.style.opacity = '0';
      setTimeout(function () { canvas.remove(); }, ms + 20);
    }

    if (!measure()) { canvas.remove(); release(); return; }
    O.hideType(el);
    release();
    draw(t0);

    function play() {
      var began = performance.now(), handed = false;
      var stop = O.onSkip(function () { finish(200); });
      function tick(now) {
        var t = t0 + now - began;
        if (t >= HAND[0] && !handed) { handed = true; O.showType(el, HAND[1] - HAND[0]); }
        if (t >= END) { stop(); finish(0); return; }
        draw(t);
        frame = requestAnimationFrame(tick);
      }
      frame = requestAnimationFrame(tick);
    }

    if (trailer) {
      var seen = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return;
        seen.disconnect();
        // data-delay waits out the home page's cut-in, counted from the page's
        // start: a sheet first seen later plays at once.
        setTimeout(play, Math.max(0, (+host.dataset.delay || 0) - performance.now()));
      }, { threshold: 0.6 });
      seen.observe(host);
    } else play();
    addEventListener('resize', function () { finish(0); });
  }

  O.register('flectobi', function (host) { start(host, false); });
  O.register('flectobi-trailer', function (host) { start(host, true); });
})(typeof globalThis !== 'undefined' ? globalThis : this);
