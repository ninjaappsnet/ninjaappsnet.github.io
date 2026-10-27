// What every title opening shares (assets/mosaic.js for Smalti, folio.js for
// Dayfolio, flecto.js for FlectoBI): the motion curves, the title set on an
// offscreen mask exactly where the page sets it, the mask read back as grid
// cells, a canvas stage, and the boot.
//
// An opening is marked in the page as data-opening="<name>" on its host (the
// one-sheet, or a sheet on the home page) and draws its host's title, which
// stays in the page for every reader. The pure parts are tested in node by
// tools/test-*.mjs; the DOM parts are skipped there.
(function (root) {
  'use strict';

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

  // Progress of a span from `from` lasting `ms`, clamped to 0..1.
  function span(time, from, ms) { return Math.min(1, Math.max(0, (time - from) / ms)); }

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

  var api = { rng: rng, bezier: bezier, easeOut: easeOut, easeInOut: easeInOut, span: span, cells: cells };
  root.NinjaOpening = api;

  // ----- in the page -----
  if (typeof document === 'undefined') return;

  api.still = function () { return matchMedia('(prefers-reduced-motion: reduce)').matches; };

  // The text node an opening draws: the title's own words.
  api.textOf = function (el) {
    var walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (var n = walk.nextNode(); n; n = walk.nextNode()) if (n.data.trim()) return n;
    return null;
  };

  // A canvas over the whole host, under its type. Its placing is set here, not
  // only in style.css: a visitor holding an older stylesheet must never get the
  // canvas in the flow of the page.
  api.stage = function (host) {
    var canvas = document.createElement('canvas');
    canvas.className = 'opening-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none';
    host.insertBefore(canvas, host.firstChild);
    var st = { canvas: canvas, ctx: canvas.getContext('2d'), dpr: 1, w: 0, h: 0 };
    st.fit = function () {
      var box = host.getBoundingClientRect();
      st.dpr = Math.min(2, window.devicePixelRatio || 1);
      st.w = box.width; st.h = box.height;
      canvas.width = Math.round(box.width * st.dpr);
      canvas.height = Math.round(box.height * st.dpr);
      st.ctx.setTransform(st.dpr, 0, 0, st.dpr, 0, 0);
      return box;
    };
    st.clear = function () { st.ctx.clearRect(0, 0, st.w, st.h); };
    return st;
  };

  // The title set on an offscreen mask exactly where the page sets it, in the
  // host's coordinates. Letters set as tight as the type would fuse on a grid,
  // so the mask sets them `spacing` em apart (null keeps the page's spacing)
  // and fits the same width, centred on the same line. Null when the face did
  // not load as the page set it.
  api.mask = function (host, el, spacing) {
    var text = api.textOf(el);
    if (!text) return null;
    var box = host.getBoundingClientRect();
    var cs = getComputedStyle(el), size = parseFloat(cs.fontSize);
    var range = document.createRange(); range.selectNodeContents(text);
    var ink = range.getBoundingClientRect();
    var mask = document.createElement('canvas');
    mask.width = Math.max(1, Math.ceil(box.width)); mask.height = Math.max(1, Math.ceil(box.height));
    var m = mask.getContext('2d', { willReadFrequently: true });
    m.font = '900 ' + size + 'px Archivo';
    var stretch = parseFloat(cs.fontStretch) || 100;
    if ('fontStretch' in m) m.fontStretch = stretch >= 120 ? 'expanded' : stretch >= 110 ? 'semi-expanded' : 'normal';
    if ('letterSpacing' in m) m.letterSpacing = cs.letterSpacing;
    var check = ink.width / m.measureText(text.data).width;
    if (!(check > 0.85 && check < 1.15)) return null;
    if (spacing !== null && 'letterSpacing' in m) m.letterSpacing = (size * spacing) + 'px';
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
    return {
      alpha: alpha, w: mask.width, h: mask.height, size: size, text: text.data,
      ink: { left: ink.left - box.left, top: mid - inkH * fit / 2, width: ink.width, height: inkH * fit },
    };
  };

  // While the canvas draws the title, the type is transparent; it is given
  // back with a short fade when the opening ends or gives up.
  api.hideType = function (el) { el.style.transition = 'none'; el.style.color = 'transparent'; };
  api.showType = function (el, ms) {
    el.style.transition = ms ? 'color ' + ms + 'ms ease' : 'none';
    el.style.color = '';
  };

  // Any wish to get on (a click, a key, a scroll or a touch) ends an opening at
  // once. Returns a function that stops listening.
  api.onSkip = function (fn) {
    var kinds = ['pointerdown', 'keydown', 'wheel', 'touchstart'];
    function go() { off(); fn(); }
    function off() { for (var i = 0; i < kinds.length; i++) removeEventListener(kinds[i], go, true); }
    for (var i = 0; i < kinds.length; i++) addEventListener(kinds[i], go, { capture: true, passive: true });
    return off;
  };

  // Openings register themselves by name; the boot starts each marked host
  // once the title face has loaded.
  var kinds = {};
  api.register = function (name, start) { kinds[name] = start; };
  function boot() {
    var hosts = document.querySelectorAll('[data-opening]');
    if (!hosts.length) return;
    var go = function () {
      for (var i = 0; i < hosts.length; i++) {
        var start = kinds[hosts[i].getAttribute('data-opening')];
        if (start) start(hosts[i]);
      }
    };
    if (document.fonts && document.fonts.load) document.fonts.load('900 100px Archivo').then(go, go);
    else go();
  }
  // Boot after every deferred script has registered: deferred scripts run
  // while the document is already "interactive", before DOMContentLoaded.
  if (document.readyState !== 'complete') document.addEventListener('DOMContentLoaded', boot);
  else setTimeout(boot, 0);
})(typeof globalThis !== 'undefined' ? globalThis : this);
