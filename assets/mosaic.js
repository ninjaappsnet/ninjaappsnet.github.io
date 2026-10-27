// Smalti's opening: the title restored as a mosaic. The name starts as empty
// slots, like the empty cells of a board in the game, and the game's pieces
// (tetrominoes and pentominoes, one glaze each) seat into them from left to
// right, each lifted, turned and a little large until it drops into place. One
// sweep of glaze light crosses the finished name, then it holds still.
//
// Three ways in, by data-opening on the host:
//   smalti   the one-sheet: the full opening; the mosaic stays as the title.
//   smalti-trailer   a sheet on the home page: a short run when the sheet is
//            first seen, then the type comes back.
//   broken   the 404: the number set whole, then a few pieces fall out of it.
//
// The real title stays in the page for every reader. Under reduced motion the
// finished mosaic is drawn at once. The plan and the timeline are pure
// functions, tested by tools/test-mosaic.mjs. Needs assets/opening.js.
(function (root) {
  'use strict';
  var O = root.NinjaOpening;

  var TILE_MS = 420;    // one tile seating
  var SWEEP_MS = 900;   // left edge to right edge
  var GLAZE_MS = 650;   // the light crossing once
  var FALL_MS = 1100;   // a loose piece dropping out of the 404

  // The game's glazes: ivory carries the name, gold and oxblood are the
  // accents of its boards, jade the odd piece.
  var GLAZE = { ivory: '#efe6d3', gold: '#d9a441', oxblood: '#a63a50', jade: '#4f9470' };
  var easeOut = O.easeOut, easeInOut = O.easeInOut;

  var SIDES = [[1, 0], [-1, 0], [0, 1], [0, -1]];

  // The cells cut into the game's pieces, exactly: every letter is tiled with
  // pieces of three to five squares (tetrominoes and pentominoes first, a
  // tromino only where nothing else fits), never one or two, as the game has
  // none. A search from left to right: the first free cell takes a piece that
  // contains it, and a choice that would strand a gap of one or two squares is
  // undone. A stray of one or two cells that no piece can hold is left out.
  // Each piece takes one glaze and seats as one.
  function plan(list, o) {
    var rand = O.rng(o.seed || 1);
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
                    delay: Math.round(80 + (px / o.width) * (o.sweep || SWEEP_MS) + j3 * 160) };
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

  // The 404: a few whole pieces work loose and fall out of the set number, one
  // after another, leaving their slots empty. Not two from the same stroke in
  // a row, and never so many that the number stops reading.
  function loosen(tiles, o) {
    var rand = O.rng(o.seed || 3), ids = [], seen = {};
    for (var i = 0; i < tiles.length; i++) if (!seen[tiles[i].piece]) { seen[tiles[i].piece] = true; ids.push(tiles[i].piece); }
    var count = Math.max(1, Math.round(ids.length * (o.share || 0.1))), chosen = {};
    for (var n = 0; n < count; n++) {
      var at = Math.floor(rand() * ids.length);
      chosen[ids[at]] = Math.round(500 + n * 260 + rand() * 120);
      ids.splice(at, 1);
    }
    return tiles.map(function (t) {
      var c = {};
      for (var k in t) c[k] = t[k];
      c.delay = -TILE_MS;   // set before the page shows
      if (chosen[t.piece] !== undefined) { c.fall = chosen[t.piece]; c.drift = Math.round((rand() - 0.5) * 60) / 100; }
      return c;
    });
  }

  function tileState(t, time) {
    if (t.fall !== undefined && time >= t.fall) {
      var f = (time - t.fall) / FALL_MS;
      if (f >= 1) return { alpha: 0, slot: true, scale: 1, lift: 0, angle: t.rest, drop: 0 };
      // Gravity: it lets go slowly, then drops; it turns as it goes and is gone
      // before it leaves the stage.
      return { alpha: 1 - Math.max(0, (f - 0.6) / 0.4), slot: true, scale: 1, lift: 0,
               angle: t.rest + t.drift * f * 3, drop: f * f };
    }
    if (time < t.delay) return { alpha: 0, slot: true, scale: 1.3, lift: 1, angle: t.rest + t.spin, drop: 0 };
    var p = (time - t.delay) / TILE_MS;
    if (p >= 1) return { alpha: 1, slot: false, scale: 1, lift: 0, angle: t.rest, drop: 0 };
    var e = easeOut(p);
    return { alpha: Math.min(1, p * 4), slot: true, scale: 1 + 0.3 * (1 - e), lift: 1 - e, angle: t.rest + t.spin * (1 - e), drop: 0 };
  }

  function duration(tiles) {
    var last = 0;
    for (var i = 0; i < tiles.length; i++) {
      last = Math.max(last, tiles[i].delay + TILE_MS);
      if (tiles[i].fall !== undefined) last = Math.max(last, tiles[i].fall + FALL_MS);
    }
    return last;
  }

  // The grid for a title of `size` px: a tile must still read as a tile, so a
  // small title (a phone, a sheet on the home page) takes fewer, larger cells.
  function cellFor(size) { return size >= 90 ? Math.max(7, size / 17) : Math.max(5, size / 11); }

  root.NinjaMosaic = {
    GLAZE: GLAZE, cells: O.cells, plan: plan, loosen: loosen, tileState: tileState, duration: duration, cellFor: cellFor,
    TILE_MS: TILE_MS, GLAZE_MS: GLAZE_MS, FALL_MS: FALL_MS,
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
    if (s >= 8) {
      g.fillStyle = 'rgba(255,255,255,.5)';
      g.beginPath(); g.ellipse(pad + s * 0.32, pad + s * 0.24, s * 0.2, s * 0.09, -0.5, 0, Math.PI * 2); g.fill();
    }
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

  function start(host, mode) {
    var el = mode === 'trailer' ? host.querySelector('.sheet-title a') : host.querySelector('h1');
    if (!el || !O.textOf(el)) return;
    var st = O.stage(host), ctx = st.ctx, canvas = st.canvas;
    var tiles = [], sprites = {}, slot = null, cell = 20, frame = 0;

    function measure() {
      st.fit();
      var mk = O.mask(host, el, 0.03);
      if (!mk || mk.size < 44) return false;
      cell = cellFor(mk.size);
      var list = O.cells(mk.alpha, mk.w, mk.h, cell);
      tiles = plan(list, { seed: 7, width: st.w, cell: cell, sweep: mode === 'trailer' ? 360 : SWEEP_MS });
      if (mode === 'broken') tiles = loosen(tiles, { seed: 3, share: 0.1 });
      var side = cell * 0.9;
      sprites = {};
      for (var k in GLAZE) sprites[GLAZE[k]] = sprite(GLAZE[k], side, st.dpr);
      slot = slotSprite(side, st.dpr);
      return tiles.length > 0;
    }

    function draw(time, glaze) {
      st.clear();
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
        ctx.translate(t.px + (dx * cos - dy * sin) * s.scale,
                      t.py + (dx * sin + dy * cos) * s.scale + s.lift * cell * 1.8 + s.drop * (st.h - t.py + cell * 4));
        ctx.rotate(s.angle);
        ctx.scale(s.scale, s.scale);
        ctx.drawImage(sp.canvas, -full / 2, -full / 2, full, full);
        if (glaze !== null) {
          var d = Math.abs(t.x / st.w - glaze);
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

    function finish() {
      cancelAnimationFrame(frame);
      if (mode === 'trailer') { canvas.remove(); O.showType(el, 0); }
      else draw(Infinity, null);
    }

    function play() {
      var began = performance.now(), end = duration(tiles), glazeMs = mode === 'broken' ? 0 : GLAZE_MS;
      var stop = O.onSkip(finish);
      function tick(now) {
        var time = now - began;
        var glaze = glazeMs && time > end ? easeInOut(Math.min(1, (time - end) / glazeMs)) * 1.3 - 0.15 : null;
        draw(time, glaze);
        if (time < end + glazeMs) frame = requestAnimationFrame(tick);
        else if (mode === 'trailer') {
          // The trailer hands the title back to the type, which takes the
          // sheet's hover and focus as it always does.
          stop();
          O.showType(el, 240);
          canvas.style.transition = 'opacity 240ms ease';
          canvas.style.opacity = '0';
          setTimeout(function () { canvas.remove(); }, 260);
        } else { stop(); draw(Infinity, null); }
      }
      frame = requestAnimationFrame(tick);
    }

    if (!measure()) { canvas.remove(); host.classList.add('opened'); return; }
    var still = O.still();
    if (mode === 'trailer') {
      if (still) { canvas.remove(); return; }
      // Plays once, when the sheet is first well in view.
      O.hideType(el);
      draw(0, null);
      var seen = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return;
        seen.disconnect();
        // data-delay waits out the home page's cut-in, counted from the page's
        // start: a sheet first seen later plays at once.
        setTimeout(play, Math.max(0, (+host.dataset.delay || 0) - performance.now()));
      }, { threshold: 0.6 });
      seen.observe(host);
      return;
    }
    O.hideType(el);
    host.classList.add('opened');
    if (still) draw(Infinity, null);
    else { draw(0, null); play(); }

    var pending = 0;
    addEventListener('resize', function () {
      clearTimeout(pending);
      pending = setTimeout(function () {
        cancelAnimationFrame(frame);
        if (measure()) draw(Infinity, null);
        else { canvas.remove(); O.showType(el, 0); }
      }, 150);
    });
  }

  O.register('smalti', function (host) { start(host, 'title'); });
  O.register('smalti-trailer', function (host) { start(host, 'trailer'); });
  O.register('broken', function (host) { start(host, 'broken'); });
})(typeof globalThis !== 'undefined' ? globalThis : this);
