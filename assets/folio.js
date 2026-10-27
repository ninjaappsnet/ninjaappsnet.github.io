// Dayfolio's opening: the title written a line a day. The name is ruled like
// a journal page, and each ruled line of its letters is inked from left to
// right, one working day after another, each dated in the margin, the last
// line today. Then the thin lines close up into solid type, and the type takes
// over: small daily notes become the report.
//
// The real <h1> stays in the page and ends visible. A click, key, scroll or
// touch ends the opening at once; under reduced motion there is none. The
// lines, dates and timeline are pure, tested by tools/test-folio.mjs. Needs
// assets/opening.js.
(function (root) {
  'use strict';
  var O = root.NinjaOpening;

  var WRITE = [150, 2000];   // every line written, top to bottom
  var CLOSE = [2000, 2350];  // the lines close up into type
  var HAND = [2350, 2650];   // the type takes over
  var END = HAND[1];
  var THIN = 0.38;           // a written line's weight, against its row
  var NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var span = O.span, easeInOut = O.easeInOut;

  // The ruled lines of the name: a line per row of `pitch` px that has ink on
  // it, each the runs of ink along its middle, left to right.
  function lines(alpha, w, h, pitch) {
    var out = [];
    for (var y = pitch / 2; y < h; y += pitch) {
      var row = Math.floor(y) * w, runs = [], open = -1;
      for (var x = 0; x <= w; x++) {
        var inked = x < w && alpha[row + x] > 127;
        if (inked && open < 0) open = x;
        if (!inked && open >= 0) { if (x - open >= 2) runs.push([open, x]); open = -1; }
      }
      if (runs.length) out.push({ y: y, runs: runs, from: runs[0][0], to: runs[runs.length - 1][1] });
    }
    return out;
  }

  // A date per line: working days running back from today (from the Friday
  // before, at a weekend), the last line today.
  function days(count, today) {
    var d = new Date(today.getFullYear(), today.getMonth(), today.getDate()), out = [];
    while (d.getDay() === 0 || d.getDay() === 6) d.setDate(d.getDate() - 1);
    while (out.length < count) {
      if (d.getDay() !== 0 && d.getDay() !== 6) out.unshift(NAMES[d.getDay()] + ' ' + d.getDate());
      d.setDate(d.getDate() - 1);
    }
    return out;
  }

  function startOf(n, count) { return WRITE[0] + n * (WRITE[1] - WRITE[0]) / count; }

  // Where the pen is on line n at time t: null before its day, then left to
  // right across the line, done when the next line starts.
  function pen(line, n, count, t) {
    var from = startOf(n, count);
    if (t < from) return null;
    var p = Math.min(1, (t - from) / ((WRITE[1] - WRITE[0]) / count));
    return line.from + (line.to - line.from) * (p * (2 - p) * 0.35 + p * 0.65);
  }

  function state(t) {
    return {
      weight: THIN + (1 - THIN) * easeInOut(span(t, CLOSE[0], CLOSE[1] - CLOSE[0])),
      date: span(t, 0, 150) * (1 - span(t, WRITE[1], 200)),
      rule: span(t, 0, 200) * (1 - span(t, CLOSE[0], 250)),
      lines: 1 - span(t, HAND[0], HAND[1] - HAND[0]),
      type: span(t, HAND[0], HAND[1] - HAND[0]),
    };
  }

  root.NinjaFolio = { lines: lines, days: days, pen: pen, startOf: startOf, state: state, WRITE: WRITE, CLOSE: CLOSE, HAND: HAND, END: END };

  // ----- in the page -----
  if (typeof document === 'undefined') return;

  function start(host, trailer) {
    var el = trailer ? host.querySelector('.sheet-title a') : host.querySelector('h1');
    if (!el || !O.textOf(el)) return;
    function release() { host.classList.add('opened'); }
    if (O.still()) { release(); return; }
    var st = O.stage(host), ctx = st.ctx, canvas = st.canvas;
    var css = getComputedStyle(host);
    var ink = css.getPropertyValue('--app-on').trim() || '#ffffff';
    var paper = css.getPropertyValue('--app-hi').trim() || '#fdf3e4';
    var speed = trailer ? 1.7 : 1;   // a home sheet writes faster
    var rows = [], dates = [], pitch = 6, box = null, margin = false, frame = 0, done = false;

    function measure() {
      st.fit();
      var mk = O.mask(host, el, null);   // the page's own spacing: the lines close up onto the type
      if (!mk) return false;
      box = mk.ink;
      pitch = Math.max(3, box.height / 13);
      rows = lines(mk.alpha, mk.w, mk.h, pitch);
      dates = days(rows.length, new Date());
      // Dates go in the margin when there is one; otherwise one date, above the name, keeps the count.
      margin = box.left >= 64;
      return rows.length > 2;
    }

    function draw(t) {
      var s = state(t), i, j;
      st.clear();
      // The ruling: a faint line across the name for every day to come.
      if (s.rule > 0) {
        ctx.fillStyle = paper; ctx.globalAlpha = 0.16 * s.rule;
        for (i = 0; i < rows.length; i++) ctx.fillRect(box.left, rows[i].y + pitch * THIN / 2, box.width, 1);
      }
      var label = '', labelY = 0, tip = null, h = pitch * s.weight + (s.weight === 1 ? 0.6 : 0);
      ctx.globalAlpha = s.lines;
      // Written in the page's cream; closing up, the lines take the type's white.
      ctx.fillStyle = s.weight > 0.8 ? ink : paper;
      for (i = 0; i < rows.length; i++) {
        var x = pen(rows[i], i, rows.length, t);
        if (x === null) break;
        for (j = 0; j < rows[i].runs.length; j++) {
          var r = rows[i].runs[j], to = Math.min(r[1], x);
          if (to > r[0]) ctx.fillRect(r[0], rows[i].y - h / 2, to - r[0], h);
        }
        label = dates[i]; labelY = rows[i].y; tip = x;
        if (margin && s.date > 0) {
          ctx.save();
          ctx.globalAlpha = s.date * (i === rows.length - 1 || pen(rows[i + 1], i + 1, rows.length, t) === null ? 1 : 0.45);
          ctx.fillStyle = paper; ctx.font = '700 ' + Math.max(9, Math.min(12, pitch * 0.9)) + 'px Archivo';
          ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
          ctx.fillText(label.toUpperCase(), box.left - 14, labelY);
          ctx.restore();
        }
      }
      // No margin (a phone, a home sheet): the date rides just ahead of the
      // pen, on the part of the line still to write.
      if (!margin && label && s.date > 0 && tip !== null) {
        ctx.save();
        ctx.globalAlpha = s.date; ctx.fillStyle = paper; ctx.font = '700 11px Archivo'; ctx.textBaseline = 'middle';
        ctx.fillText(label.toUpperCase(), Math.min(tip + 6, box.left + box.width + 6), labelY);
        ctx.restore();
      }
      ctx.globalAlpha = 1;
    }

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
    draw(0);

    function play() {
      var began = performance.now(), handed = false;
      var stop = O.onSkip(function () { finish(200); });
      function tick(now) {
        var t = (now - began) * speed;
        if (t >= HAND[0] && !handed) { handed = true; O.showType(el, (HAND[1] - HAND[0]) / speed); }
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

  O.register('dayfolio', function (host) { start(host, false); });
  O.register('dayfolio-trailer', function (host) { start(host, true); });
})(typeof globalThis !== 'undefined' ? globalThis : this);
