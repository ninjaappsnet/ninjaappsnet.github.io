// The opening of Smalti's one-sheet: the title is restored as a mosaic. The
// name starts as empty slots, like the empty cells of a board in the game, and
// the game's pieces (tetrominoes and pentominoes, one glaze each) seat into
// them from left to right, each lifted, turned and a little large until it
// drops into place. One sweep of glaze light crosses the
// finished name, then it holds still.
//
// The real <h1> stays in the page for every reader. With no script the title
// is plain type (the page only hides it under html.js); if this script fails,
// style.css brings the type back after three seconds. Under reduced motion the
// finished mosaic is drawn at once. The cells, the plan and the timeline are
// pure functions, tested by tools/test-mosaic.mjs.
(function (root) {
  'use strict';

  var TILE_MS = 420;    // one tile seating
  var SWEEP_MS = 900;   // left edge to right edge
  var GLAZE_MS = 650;   // the light crossing once

  // The game's glazes: ivory carries the name, gold and oxblood are the
  // accents of its boards, jade the odd piece.
  var GLAZE = { ivory: '#efe6d3', gold: '#d9a441', oxblood: '#a63a50', jade: '#4f9470' };

  function rng(seed) {
    var s = seed >>> 0 || 1;
    return function () {
      s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0;
      return s / 4294967296;
    };
  }

  // cubic-bezier(x1, y1, x2, y2) as a function of progress, solved for x.
  function bezier(x1, y1, x2, y2) {
    function a(p1, p2) { return 1 - 3 * p2 + 3 * p1; }
    function b(p1, p2) { return 3 * p2 - 6 * p1; }
    function c(p1) { return 3 * p1; }
    function at(t, p1, p2) { return ((a(p1, p2) * t + b(p1, p2)) * t + c(p1)) * t; }
    function slope(t, p1, p2) { return 3 * a(p1, p2) * t * t + 2 * b(p1, p2) * t + c(p1); }
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      var t = x;
      for (var i = 0; i < 8; i++) {
        var d = slope(t, x1, x2);
        if (Math.abs(d) < 1e-6) break;
        t -= (at(t, x1, x2) - x) / d;
      }
      return at(Math.min(1, Math.max(0, t)), y1, y2);
    };
  }
  var easeOut = bezier(0.23, 1, 0.32, 1);      // --ease-out
  var easeInOut = bezier(0.77, 0, 0.175, 1);   // --ease-in-out

  // The cells of a square grid that the inked mask covers at least half of.
  function cells(alpha, width, height, size) {
    var out = [], step = size / 5;
    for (var cy = size / 2; cy < height; cy += size) {
      for (var cx = size / 2; cx < width; cx += size) {
        var hit = 0;
        for (var sy = 0; sy < 5; sy++) {
          for (var sx = 0; sx < 5; sx++) {
            var x = Math.floor(cx - size / 2 + step * (sx + 0.5)), y = Math.floor(cy - size / 2 + step * (sy + 0.5));
            if (x >= 0 && y >= 0 && x < width && y < height && alpha[y * width + x] > 127) hit++;
          }
        }
        if (hit >= 13) out.push({ x: cx, y: cy, i: Math.round((cx - size / 2) / size), j: Math.round((cy - size / 2) / size) });
      }
    }
    return out;
  }

  var SIDES = [[1, 0], [-1, 0], [0, 1], [0, -1]];

  // The cells cut into the game's pieces, exactly: every letter is tiled with
  // pieces of three to five squares (tetrominoes and pentominoes first, a
  // tromino only where nothing else fits), never one or two, as the game has
  // none. A search from left to right: the first free cell takes a piece that
  // contains it, and a choice that would strand a gap of one or two squares is
  // undone. A stray of one or two cells that no piece can hold is left out.
  // Each piece takes one glaze and seats as one.
  function plan(list, o) {
    var rand = rng(o.seed || 1);
    var order = list.slice().sort(function (a, b) { return a.i - b.i || a.j - b.j; });
    var at = {}, rank = {}, owner = {};
    for (var n = 0; n < order.length; n++) {
      var key0 = order[n].i + ',' + order[n].j;
      at[key0] = order[n]; rank[key0] = n;
    }
    function k(c) { return c.i + ',' + c.j; }
    function free(key) { return at[key] !== undefined && owner[key] === undefined; }

    // The free region around a cell, counted up to `cap`.
    function reach(start, cap) {
      var seen = {}, todo = [start], count = 0;
      seen[start] = true;
      while (todo.length && count < cap) {
        var c = at[todo.pop()]; count++;
        for (var d = 0; d < 4; d++) {
          var nk = (c.i + SIDES[d][0]) + ',' + (c.j + SIDES[d][1]);
          if (!seen[nk] && free(nk)) { seen[nk] = true; todo.push(nk); }
        }
      }
      return count;
    }

    // Every connected set of `size` free cells that holds `first` and no cell
    // before it, so each placement is found once.
    function shapes(first, size) {
      var out = [], found = {}, base = rank[first];
      (function grow(set) {
        if (set.length === size) {
          var id = set.slice().sort().join('|');
          if (!found[id]) { found[id] = true; out.push(set.slice()); }
          return;
        }
        for (var s2 = 0; s2 < set.length; s2++) {
          var c = at[set[s2]];
          for (var d = 0; d < 4; d++) {
            var nk = (c.i + SIDES[d][0]) + ',' + (c.j + SIDES[d][1]);
            if (free(nk) && rank[nk] > base && set.indexOf(nk) < 0) { set.push(nk); grow(set); set.pop(); }
          }
        }
      })([first]);
      return out;
    }

    var pieces = [], steps = 0, LIMIT = 200000;
    function strands(cells) {
      for (var c2 = 0; c2 < cells.length; c2++) {
        var c = at[cells[c2]];
        for (var d = 0; d < 4; d++) {
          var nk = (c.i + SIDES[d][0]) + ',' + (c.j + SIDES[d][1]);
          if (free(nk) && reach(nk, 3) < 3) return true;
        }
      }
      return false;
    }
    function solve(from) {
      while (from < order.length && !free(k(order[from]))) from++;
      if (from >= order.length) return true;
      if (++steps > LIMIT) return false;
      var first = k(order[from]);
      if (reach(first, 3) < 3) { owner[first] = -1; if (solve(from + 1)) return true; delete owner[first]; return false; }
      var sizes = rand() < 0.5 ? [5, 4, 3] : [4, 5, 3], options = [];
      for (var z = 0; z < 3; z++) {
        var found = shapes(first, sizes[z]);
        for (var f = found.length - 1; f > 0; f--) { var r = Math.floor(rand() * (f + 1)), tmp = found[f]; found[f] = found[r]; found[r] = tmp; }
        options = options.concat(found);
      }
      for (var p = 0; p < options.length; p++) {
        var cells = options[p], id = pieces.length;
        for (var q = 0; q < cells.length; q++) owner[cells[q]] = id;
        pieces.push(cells);
        if (!strands(cells) && solve(from + 1)) return true;
        pieces.pop();
        for (q = 0; q < cells.length; q++) delete owner[cells[q]];
        if (steps > LIMIT) return false;
      }
      return false;
    }
    if (!solve(0)) {
      // The search ran out of time: lay what it can, never a piece under three.
      pieces = []; owner = {};
      for (n = 0; n < order.length; n++) {
        var start = k(order[n]);
        if (!free(start)) continue;
        var piece = [start], id3 = pieces.length;
        owner[start] = id3;
        for (var grow = 0; grow < 4 && piece.length < 5; grow++) {
          var c3 = at[piece[piece.length - 1]];
          for (var d3 = 0; d3 < 4; d3++) {
            var nk3 = (c3.i + SIDES[d3][0]) + ',' + (c3.j + SIDES[d3][1]);
            if (free(nk3)) { owner[nk3] = id3; piece.push(nk3); break; }
          }
        }
        if (piece.length < 3) { for (var x3 = 0; x3 < piece.length; x3++) owner[piece[x3]] = -1; piece = []; }
        pieces.push(piece);
      }
    }
    // Pieces as cell lists, the strays (owner -1) dropped.
    for (n = 0; n < pieces.length; n++) pieces[n] = pieces[n].map(function (key) { return at[key]; });
    for (var key1 in owner) if (owner[key1] === -1) delete at[key1];
    order = order.filter(function (c) { return at[k(c)] !== undefined; });

    var tiles = [], colour = {};
    function touchesColour(pc, self) {
      for (var x = 0; x < pc.length; x++) {
        var dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
        for (var d = 0; d < 4; d++) {
          var nb = owner[(pc[x].i + dirs[d][0]) + ',' + (pc[x].j + dirs[d][1])];
          if (nb !== undefined && nb !== self && colour[nb] && colour[nb] !== GLAZE.ivory) return true;
        }
      }
      return false;
    }
    var meta = [];
    for (var id2 = 0; id2 < pieces.length; id2++) {
      var pc = pieces[id2];
      if (!pc.length) continue;
      var px = 0, py = 0;
      for (var k2 = 0; k2 < pc.length; k2++) { px += pc[k2].x; py += pc[k2].y; }
      px = Math.round(px / pc.length * 100) / 100; py = Math.round(py / pc.length * 100) / 100;
      var j1 = rand(), j2 = rand(), j3 = rand();
      var color = j1 < 0.14 ? GLAZE.gold : j1 < 0.26 ? GLAZE.oxblood : j1 < 0.34 ? GLAZE.jade : GLAZE.ivory;
      // A coloured piece is set in ivory: next to a coloured neighbour it stays
      // ivory, so every coloured shape is outlined and reads as its piece.
      if (color !== GLAZE.ivory && touchesColour(pc, id2)) color = GLAZE.ivory;
      colour[id2] = color;
      meta[id2] = { px: px, py: py, spin: Math.round((j2 - 0.5) * 1.4 * 1000) / 1000,   // the turn it makes as it seats
                    delay: Math.round(80 + (px / o.width) * SWEEP_MS + j3 * 160) };
    }

    // Every letter carries colour: each separate stroke (cells joined side to
    // side or corner to corner) of eight cells or more that the roll left all
    // ivory takes one, on its largest piece that touches no colour.
    var accents = [GLAZE.gold, GLAZE.oxblood, GLAZE.jade], seen = {}, stroke = 0;
    for (n = 0; n < order.length; n++) {
      var startKey = order[n].i + ',' + order[n].j;
      if (seen[startKey]) continue;
      var group = [], todo = [order[n]];
      seen[startKey] = true;
      while (todo.length) {
        var cur = todo.pop();
        group.push(cur);
        for (var di = -1; di <= 1; di++) for (var dj = -1; dj <= 1; dj++) {
          var nk = (cur.i + di) + ',' + (cur.j + dj);
          if (at[nk] && !seen[nk]) { seen[nk] = true; todo.push(at[nk]); }
        }
      }
      if (group.length < 8) continue;
      var ids = {}, hasColour = false;
      for (var g = 0; g < group.length; g++) {
        var pid = owner[group[g].i + ',' + group[g].j];
        ids[pid] = true;
        if (colour[pid] !== GLAZE.ivory) hasColour = true;
      }
      if (hasColour) continue;
      var best = -1;
      for (var idk in ids) {
        var cand = +idk;
        if (touchesColour(pieces[cand], cand)) continue;
        if (best < 0 || pieces[cand].length > pieces[best].length) best = cand;
      }
      if (best >= 0) colour[best] = accents[stroke % accents.length];
      stroke++;
    }

    for (id2 = 0; id2 < pieces.length; id2++) {
      pc = pieces[id2];
      if (!pc.length) continue;
      var mt = meta[id2];
      for (k2 = 0; k2 < pc.length; k2++) {
        tiles.push({ x: pc[k2].x, y: pc[k2].y, i: pc[k2].i, j: pc[k2].j, piece: id2, px: mt.px, py: mt.py,
                     color: colour[id2], spin: mt.spin, rest: 0, delay: mt.delay });
      }
    }
    return tiles;
  }

  function tileState(t, time) {
    if (time < t.delay) return { alpha: 0, slot: true, scale: 1.3, lift: 1, angle: t.rest + t.spin };
    var p = (time - t.delay) / TILE_MS;
    if (p >= 1) return { alpha: 1, slot: false, scale: 1, lift: 0, angle: t.rest };
    var e = easeOut(p);
    return { alpha: Math.min(1, p * 4), slot: true, scale: 1 + 0.3 * (1 - e), lift: 1 - e, angle: t.rest + t.spin * (1 - e) };
  }

  function duration(tiles) {
    var last = 0;
    for (var i = 0; i < tiles.length; i++) last = Math.max(last, tiles[i].delay);
    return last + TILE_MS;
  }

  root.NinjaMosaic = {
    GLAZE: GLAZE, cells: cells, plan: plan, tileState: tileState, duration: duration,
    TILE_MS: TILE_MS, GLAZE_MS: GLAZE_MS,
  };

  // ----- in the page -----
  if (typeof document === 'undefined') return;

  function rounded(ctx, x, y, w, h, r) {
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h);
  }

  // A glazed tile drawn once per colour, as the game draws them: a body, light
  // from above, a darker foot, a gloss spot, and a soft shadow under it.
  function sprite(color, side, dpr) {
    var pad = Math.ceil(side * 0.35), s = side, c = document.createElement('canvas');
    c.width = c.height = Math.ceil((s + pad * 2) * dpr);
    var g = c.getContext('2d');
    g.scale(dpr, dpr);
    var r = s * 0.2;
    g.save();
    g.shadowColor = 'rgba(0,0,0,.45)'; g.shadowBlur = s * 0.25; g.shadowOffsetY = s * 0.12;
    g.fillStyle = color; rounded(g, pad, pad, s, s, r); g.fill();
    g.restore();
    var body = g.createLinearGradient(0, pad, 0, pad + s);
    body.addColorStop(0, 'rgba(255,255,255,.30)'); body.addColorStop(0.45, 'rgba(255,255,255,0)');
    body.addColorStop(1, 'rgba(0,0,0,.22)');
    g.fillStyle = body; rounded(g, pad, pad, s, s, r); g.fill();
    g.strokeStyle = 'rgba(0,0,0,.18)'; g.lineWidth = Math.max(1, s * 0.04); rounded(g, pad, pad, s, s, r); g.stroke();
    g.fillStyle = 'rgba(255,255,255,.5)';
    g.beginPath(); g.ellipse(pad + s * 0.32, pad + s * 0.24, s * 0.2, s * 0.09, -0.5, 0, Math.PI * 2); g.fill();
    return { canvas: c, pad: pad, side: s };
  }

  function slotSprite(side, dpr) {
    var c = document.createElement('canvas');
    c.width = c.height = Math.ceil(side * dpr);
    var g = c.getContext('2d');
    g.scale(dpr, dpr);
    g.fillStyle = 'rgba(255,255,255,.07)'; rounded(g, 0, 0, side, side, side * 0.2); g.fill();
    g.strokeStyle = 'rgba(255,255,255,.12)'; g.lineWidth = 1; rounded(g, 0.5, 0.5, side - 1, side - 1, side * 0.2); g.stroke();
    return c;
  }

  function start(host) {
    var h1 = host.querySelector('.onesheet-title');
    var text = h1 && h1.firstChild;
    if (!text || text.nodeType !== 3) return;
    var canvas = document.createElement('canvas');
    canvas.className = 'mosaic-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    // Its placing is set here, not only in style.css: a visitor holding an
    // older stylesheet must never get the canvas in the flow of the page.
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none';
    var ctx = canvas.getContext('2d');
    var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var tiles = [], sprites = {}, slot = null, cell = 20, frame = 0, width = 0, dpr = 1;

    // The name, set on an offscreen mask exactly where the page sets it, then
    // read back as grid cells.
    function measure() {
      var box = host.getBoundingClientRect();
      var cs = getComputedStyle(h1), size = parseFloat(cs.fontSize);
      var range = document.createRange(); range.selectNodeContents(text);
      var ink = range.getBoundingClientRect();
      dpr = Math.min(2, window.devicePixelRatio || 1);
      width = box.width;
      canvas.width = Math.round(box.width * dpr);
      canvas.height = Math.round(box.height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Below this size a tile is too small to read as a tile: phones keep the type.
      if (size < 90) return false;
      var mask = document.createElement('canvas');
      mask.width = Math.ceil(box.width); mask.height = Math.ceil(box.height);
      var m = mask.getContext('2d', { willReadFrequently: true });
      m.font = '900 ' + size + 'px Archivo';
      if ('fontStretch' in m) m.fontStretch = 'expanded';
      // Check the face against the page first, at the page's own spacing.
      if ('letterSpacing' in m) m.letterSpacing = cs.letterSpacing;
      var check = ink.width / m.measureText(text.data).width;
      if (!(check > 0.85 && check < 1.15)) return false;   // the face did not load as the page set it
      // On a grid, letters set as tight as the type would fuse; the mosaic sets
      // them a little apart and fits the same width, centred on the same line.
      if ('letterSpacing' in m) m.letterSpacing = (size * 0.03) + 'px';
      var metrics = m.measureText(text.data);
      var fit = ink.width / metrics.width;
      var inkH = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
      var mid = ink.top - box.top + ink.height / 2;
      m.save();
      m.translate(ink.left - box.left, mid);
      m.scale(fit, fit);
      m.fillText(text.data, 0, inkH / 2 - metrics.actualBoundingBoxDescent);
      m.restore();
      var data = m.getImageData(0, 0, mask.width, mask.height).data;
      var alpha = new Uint8ClampedArray(mask.width * mask.height);
      for (var i = 0; i < alpha.length; i++) alpha[i] = data[i * 4 + 3];

      cell = Math.max(7, size / 17);
      tiles = plan(cells(alpha, mask.width, mask.height, cell), { seed: 7, width: box.width, cell: cell });
      var side = cell * 0.9;
      sprites = {};
      for (var k in GLAZE) sprites[GLAZE[k]] = sprite(GLAZE[k], side, dpr);
      slot = slotSprite(side, dpr);
      return tiles.length > 0;
    }

    function draw(time, glaze) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      var side = cell * 0.9;
      for (var i = 0; i < tiles.length; i++) {
        var t = tiles[i], s = tileState(t, time);
        if (s.slot) ctx.drawImage(slot, t.x - side / 2, t.y - side / 2, side, side);
        if (s.alpha === 0) continue;
        var sp = sprites[t.color], full = sp.side + sp.pad * 2;
        // A piece moves as one: each tile turns and scales about the piece's centre.
        var dx = t.x - t.px, dy = t.y - t.py, cos = Math.cos(s.angle), sin = Math.sin(s.angle);
        ctx.save();
        ctx.globalAlpha = s.alpha;
        ctx.translate(t.px + (dx * cos - dy * sin) * s.scale, t.py + (dx * sin + dy * cos) * s.scale + s.lift * cell * 1.8);
        ctx.rotate(s.angle);
        ctx.scale(s.scale, s.scale);
        ctx.drawImage(sp.canvas, -full / 2, -full / 2, full, full);
        if (glaze !== null) {
          var d = Math.abs(t.x / width - glaze);
          if (d < 0.07) {
            ctx.globalAlpha = 0.55 * (1 - d / 0.07);
            ctx.fillStyle = '#fff';
            rounded(ctx, -side / 2, -side / 2, side, side, side * 0.2);
            ctx.fill();
          }
        }
        ctx.restore();
      }
    }

    function play() {
      var began = performance.now(), end = duration(tiles);
      function tick(now) {
        var time = now - began;
        var glaze = time > end ? easeInOut(Math.min(1, (time - end) / GLAZE_MS)) * 1.3 - 0.15 : null;
        draw(time, glaze);
        if (time < end + GLAZE_MS) frame = requestAnimationFrame(tick);
        else draw(Infinity, null);
      }
      frame = requestAnimationFrame(tick);
    }

    host.insertBefore(canvas, host.firstChild);
    if (!measure()) { canvas.remove(); h1.classList.add('untiled'); return; }
    h1.classList.add('tiled');
    h1.style.color = 'transparent';
    if (still) draw(Infinity, null);
    else { draw(0, null); play(); }

    var pending = 0;
    addEventListener('resize', function () {
      clearTimeout(pending);
      pending = setTimeout(function () {
        cancelAnimationFrame(frame);
        if (measure()) draw(Infinity, null);
        else { canvas.remove(); h1.classList.remove('tiled'); h1.classList.add('untiled'); h1.style.color = ''; }
      }, 150);
    });
  }

  function boot() {
    var hosts = document.querySelectorAll('[data-mosaic]');
    var go = function () { for (var i = 0; i < hosts.length; i++) start(hosts[i]); };
    if (!hosts.length) return;
    if (document.fonts && document.fonts.load) document.fonts.load('900 100px Archivo').then(go, go);
    else go();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})(typeof globalThis !== 'undefined' ? globalThis : this);
