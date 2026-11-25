(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const NS = 'http://www.w3.org/2000/svg';

  /* ---------- Where this visitor came from, sent with every enquiry ---------- */
  const LIVE = /^https?:$/.test(location.protocol) && !/claude/.test(location.hostname);
  const KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  let track = {};
  try { track = JSON.parse(sessionStorage.getItem('al_track') || '{}'); } catch (e) { track = {}; }
  const qs = new URLSearchParams(location.search);
  if (KEYS.some(k => qs.get(k)) || qs.get('fbclid') || qs.get('gclid') || !track.landing_page) {
    track = { landing_page: location.pathname + location.search, referrer: document.referrer };
    KEYS.forEach(k => { if (qs.get(k)) track[k] = qs.get(k); });
    if (qs.get('fbclid') && !track.utm_source) track.utm_source = 'facebook';
    if (qs.get('gclid') && !track.utm_source) track.utm_source = 'google';
  }
  try { sessionStorage.setItem('al_track', JSON.stringify(track)); } catch (e) { /* private mode */ }
  function leadSource() {
    const s = (track.utm_source || '').toLowerCase(), r = (track.referrer || '').toLowerCase();
    if (/chatgpt|openai/.test(s) || /chatgpt\.com|openai\.com/.test(r)) return 'ChatGPT ad';
    if (/facebook|^fb$|meta|instagram/.test(s) || /facebook\.|instagram\./.test(r)) return 'Facebook';
    if (/youtube/.test(s) || /youtube\./.test(r)) return 'YouTube';
    if (/google/.test(s) || /google\./.test(r)) return 'Google';
    if (s) return s;
    const host = r.replace(/^https?:\/\//, '').split('/')[0];
    return host && host !== location.hostname ? 'Link from ' + host : 'Website';
  }
  function stamp(form, subject) {
    const set = (n, v) => { const el = form.querySelector(`input[type="hidden"][name="${n}"]`); if (el) el.value = v || ''; };
    const src = leadSource();
    set('lead_source', src);
    KEYS.concat(['landing_page', 'referrer']).forEach(k => set(k, track[k]));
    set('subject', `${subject} | ${src}`);
  }
  async function send(form, files) {
    if (!LIVE) { await new Promise(r => setTimeout(r, 400)); return; }
    const fd = new FormData(form);
    ['photo1', 'photo2', 'photo3'].forEach(k => fd.delete(k));
    const opts = { method: 'POST' };
    if (form.querySelector('input[type="file"][name]')) {
      (files || []).forEach((b, i) => fd.append('photo' + (i + 1), b, `photo${i + 1}.jpg`));
      opts.body = fd;
    } else {
      opts.headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
      opts.body = new URLSearchParams([...fd].filter(([, v]) => typeof v === 'string')).toString();
    }
    const res = await fetch('/', opts);
    if (!res.ok) throw new Error('Form answered ' + res.status);
  }
  function busy(btn, on) {
    if (!btn) return;
    const label = btn.firstChild;
    if (on) { btn.dataset.label = label.textContent; label.textContent = 'Sending '; btn.disabled = true; btn.setAttribute('aria-busy', 'true'); }
    else { if (btn.dataset.label) label.textContent = btn.dataset.label; btn.disabled = false; btn.removeAttribute('aria-busy'); }
  }
  const FAIL = 'That didn’t send. Please try again, or call or text me at 250 514 8944.';

  /* ---------- Navigation: full height menu on phones ---------- */
  const menuBtn = $('.menu-btn'), menu = $('#menu');
  function setMenu(open) {
    if (!menu) return;
    menuBtn.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('open', open);
    menu.inert = !open;
    document.documentElement.style.overflow = open ? 'hidden' : '';
    if (open) $('a', menu).focus({ preventScroll: true });
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', () => setMenu(menuBtn.getAttribute('aria-expanded') !== 'true'));
    $$('a', menu).forEach(a => a.addEventListener('click', () => setMenu(false)));
    addEventListener('keydown', e => { if (e.key === 'Escape' && menu.classList.contains('open')) { setMenu(false); menuBtn.focus(); } });
    matchMedia('(min-width: 960px)').addEventListener('change', e => { if (e.matches) setMenu(false); });
  }

  /* ---------- Scroll reveals: armed only below the fold, played once ---------- */
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.remove('pending'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    $$('[data-reveal]').forEach(n => {
      if (n.getBoundingClientRect().top > innerHeight * 0.92) { n.classList.add('pending'); io.observe(n); }
    });
  }

  /* One rAF throttled scroll loop shared by the tagline, the chart and the boat list */
  const onFrame = [];
  let ticking = false;
  const run = () => { ticking = false; onFrame.forEach(f => f()); };
  const kick = () => { if (!ticking) { ticking = true; requestAnimationFrame(run); } };
  addEventListener('scroll', kick, { passive: true });
  addEventListener('resize', kick);

  /* ---------- Tagline: words light up one at a time, in reading order ---------- */
  const tl = $('[data-split]');
  if (tl) {
    const parts = tl.innerHTML.split(/(<br>)/);
    tl.setAttribute('aria-label', tl.textContent.replace(/\s+/g, ' ').trim());
    tl.innerHTML = parts.map(p => p === '<br>' ? '<br>' : p.split(/(\s+)/).map(w => (/^\s+$/.test(w) || !w) ? w : `<span class="w" aria-hidden="true">${w}</span>`).join('')).join('');
    const words = $$('.w', tl);
    if (reduce) words.forEach(w => w.classList.add('on'));
    else onFrame.push(() => {
      const r = tl.getBoundingClientRect();
      const startTop = innerHeight * 0.85, endTop = innerHeight * 0.45 - r.height;
      const p = Math.min(1, Math.max(0, (startTop - r.top) / (startTop - endTop)));
      const n = Math.round(p * words.length);
      words.forEach((w, i) => w.classList.toggle('on', i < n));
    });
  }

  /* ---------- The passage plan: a route through the waypoints, a boat that follows the reader ---------- */
  const chartEl = $('[data-chart]');
  if (chartEl) {
    const svg = $('[data-route]', chartEl);
    const legs = $$('.leg', chartEl);
    const markers = legs.map(l => $('[data-marker]', l));
    const startEl = $('[data-end="start"]', chartEl), endEl = $('[data-end="end"]', chartEl);
    let path, clipRect, boat, samples = [], ys = [], markerL = [], total = 0, H = 0, ready = false;

    const box = (n, c) => { const r = n.getBoundingClientRect(); return { x: r.left - c.left + r.width / 2, y: r.top - c.top + r.height / 2, top: r.top - c.top, bottom: r.bottom - c.top }; };
    const el = (tag, attrs, parent) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };

    function smooth(pts) {
      let d = `M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`;
      for (let i = 0; i < pts.length - 1; i++) {
        const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2, t = 1 / 6;
        d += ` C${(p1.x + (p2.x - p0.x) * t).toFixed(1)},${(p1.y + (p2.y - p0.y) * t).toFixed(1)} ${(p2.x - (p3.x - p1.x) * t).toFixed(1)},${(p2.y - (p3.y - p1.y) * t).toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`;
      }
      return d;
    }

    function build() {
      const c = chartEl.getBoundingClientRect();
      const W = c.width; H = c.height;
      const wide = innerWidth >= 768;
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
      svg.textContent = '';
      const m = markers.map(n => box(n, c));
      const s = box(startEl, c), e = box(endEl, c);
      const start = wide ? { x: s.x, y: s.bottom + 12 } : { x: m[0].x, y: s.top };
      const end = wide ? { x: e.x, y: e.top - 12 } : { x: m[m.length - 1].x, y: e.bottom };
      const way = [start, ...m, end];
      const amp = wide ? 44 : 10;
      const pts = [];
      way.forEach((p, i) => {
        pts.push(p);
        const q = way[i + 1];
        if (q) pts.push({ x: (p.x + q.x) / 2 + (i % 2 ? amp : -amp), y: (p.y + q.y) / 2 });
      });
      const d = smooth(pts);
      const defs = el('defs', {}, svg);
      const clip = el('clipPath', { id: 'route-clip' }, defs);
      clipRect = el('rect', { x: -80, y: 0, width: W + 160, height: H, transform: 'scale(1 0)' }, clip);
      el('path', { class: 'base', d }, svg);
      path = el('path', { class: 'done', d, 'clip-path': 'url(#route-clip)' }, svg);

      /* the way back from the decision point */
      const di = legs.findIndex(l => l.classList.contains('decision'));
      if (wide && di > -1) {
        const D = m[di];
        const tx = D.x + 150, ty = D.y - 34, cx = D.x + 130, cy = D.y + 8;
        el('path', { class: 'turn', d: `M${D.x + 20},${D.y + 2} C${D.x + 70},${D.y + 20} ${cx},${cy} ${tx},${ty}` }, svg);
        const ang = Math.atan2(ty - cy, tx - cx) * 180 / Math.PI;
        el('path', { class: 'turn-head', d: 'M-2,-6 L10,0 L-2,6 Z', transform: `translate(${tx} ${ty}) rotate(${ang.toFixed(1)})` }, svg);
        const t = el('text', { class: 'turn-label caption-4', x: tx + 18, y: ty - 2 }, svg);
        el('tspan', { x: tx + 18, dy: 0 }, t).textContent = 'Turn back here';
        el('tspan', { x: tx + 18, dy: 16 }, t).textContent = 'at no cost';
      }

      /* depth soundings in the open water beside each waypoint */
      if (wide) {
        const depths = [['18', '24'], ['31', '27'], ['12', '21'], ['33', '15'], ['9', '26'], ['20', '14']];
        legs.forEach((leg, i) => {
          if (i === 0 || i === legs.length - 1 || leg.classList.contains('decision')) return;
          const card = box($('.wp', leg), c);
          const ex = W - card.x, y = m[i].y;
          [[-90, -10], [70, 22]].forEach(([dx, dy], k) => {
            el('text', { class: 'sounding caption-5', x: (ex + dx).toFixed(0), y: (y + dy).toFixed(0), 'text-anchor': 'middle' }, svg).textContent = depths[i % depths.length][k];
          });
        });
      }

      /* on phones: depth soundings and small islets in the water between the cards */
      if (!wide) {
        const depths = ['14', '22', '9', '31', '18', '26', '12'];
        legs.forEach((leg, i) => {
          const next = legs[i + 1];
          if (!next) return;
          const a = box($('.wp', leg), c), b2 = box($('.wp', next), c), gy = (a.bottom + b2.top) / 2;
          [[0.42, i], [0.8, i + 3]].forEach(([fx, k]) => {
            el('text', { class: 'sounding caption-5', x: (W * fx).toFixed(0), y: (gy + 4).toFixed(0), 'text-anchor': 'middle' }, svg).textContent = depths[k % depths.length];
          });
          if (i === 1 || i === 3) el('ellipse', { class: 'islet', cx: (W * 0.62).toFixed(0), cy: gy.toFixed(0), rx: 10, ry: 5 }, svg);
        });
      }

      boat = el('g', { class: 'boat' }, svg);
      const inner = el('g', { transform: wide ? 'scale(1.6)' : 'scale(1.2)' }, boat);
      el('circle', { class: 'halo', r: 15 }, inner);
      el('path', { class: 'wake', d: 'M-15 -4 L-28 -10 M-15 4 L-28 10' }, inner);
      el('path', { class: 'hull', d: 'M12 0 C 9 -5, -4 -6, -10 -5 L -10 5 C -4 6, 9 5, 12 0 Z' }, inner);
      el('rect', { class: 'cabin', x: -5, y: -2.5, width: 8, height: 5, rx: 1.5 }, inner);

      total = path.getTotalLength();
      const N = 360;
      samples = []; ys = [];
      for (let i = 0; i <= N; i++) {
        const l = total * i / N, p = path.getPointAtLength(l);
        samples.push(l);
        ys.push(i ? Math.max(ys[i - 1], p.y) : p.y);
      }
      markerL = m.map(pt => {
        let best = 0, bd = Infinity;
        for (let i = 0; i <= N; i++) { const p = path.getPointAtLength(samples[i]); const dd = (p.x - pt.x) ** 2 + (p.y - pt.y) ** 2; if (dd < bd) { bd = dd; best = i; } }
        return samples[best];
      });
      ready = true;
      place();
    }

    function lengthAtY(y) {
      if (y <= ys[0]) return 0;
      const N = ys.length - 1;
      if (y >= ys[N]) return total;
      let lo = 0, hi = N;
      while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (ys[mid] <= y) lo = mid; else hi = mid; }
      const f = (y - ys[lo]) / ((ys[hi] - ys[lo]) || 1);
      return samples[lo] + f * (samples[hi] - samples[lo]);
    }

    function place() {
      if (!ready) return;
      const c = chartEl.getBoundingClientRect();
      if (c.bottom < -200 || c.top > innerHeight + 200) return;
      const l = reduce ? 0 : lengthAtY(innerHeight * 0.55 - c.top);
      const p = path.getPointAtLength(l), a = path.getPointAtLength(Math.max(0, l - 2)), b = path.getPointAtLength(Math.min(total, l + 2));
      const ang = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
      boat.setAttribute('transform', `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)}) rotate(${ang.toFixed(1)})`);
      clipRect.setAttribute('transform', `scale(1 ${Math.max(0, p.y / H).toFixed(4)})`);
      legs.forEach((leg, i) => leg.classList.toggle('on', l >= markerL[i] - 1));
    }

    let rq = 0;
    const rebuild = () => { cancelAnimationFrame(rq); rq = requestAnimationFrame(build); };
    if ('ResizeObserver' in window) new ResizeObserver(rebuild).observe(chartEl);
    if (document.fonts) document.fonts.ready.then(rebuild);
    rebuild();
    onFrame.push(place);
  }

  /* ---------- Boats page: Van Isle's current listings; the row in focus sets the photograph ---------- */
  const list = $('[data-boats]');
  const photo = $('.boats-photo');
  if (list && photo) {
    let rows = $$('.boat', list), pics = $$('[data-boat-img]', photo), on = 0;
    const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const activate = i => {
      if (i === on) return; on = i;
      rows.forEach((r, k) => r.classList.toggle('is-on', k === i));
      pics.forEach((m, k) => m.classList.toggle('is-on', k === i));
    };
    const render = boats => {
      const bits = boats.map(b => ({
        name: `${b.year || ''} ${b.title || ''}`.trim(),
        price: b.price || 'Call for price',
        status: /^active$/i.test(b.status || 'Active') ? '' : b.status,
        b
      }));
      photo.innerHTML = bits.map((x, i) => `<img data-boat-img="${i}" src="${esc(x.b.image)}" width="1200" height="800" ${i ? 'loading="lazy"' : ''} referrerpolicy="no-referrer" alt="${esc(x.name)}"${i ? '' : ' class="is-on"'}>`).join('');
      list.innerHTML = bits.map((x, i) => `<li class="boat${i ? '' : ' is-on'}" data-i="${i}"><span class="boat-name title-2">${esc(x.name)}</span><span class="boat-price title-2">${esc(x.price)}</span><span class="boat-spec body-6">${esc(x.b.length)}${x.status ? ` <span class="tag caption-4">${esc(x.status)}</span>` : ''}</span><span class="boat-act"><button type="button" class="link-btn button-sm" data-ask="${esc(x.name)}" data-price="${esc(x.price)}" data-url="${esc(x.b.url)}">Ask me about her</button><a class="body-5" href="${esc(x.b.url)}" target="_blank" rel="noopener">Full listing and photos</a></span></li>`).join('');
      rows = $$('.boat', list); pics = $$('[data-boat-img]', photo); on = 0;
      kick();
    };
    list.addEventListener('pointerover', e => { const r = e.target.closest('.boat'); if (r && e.pointerType === 'mouse') activate(+r.dataset.i); });
    list.addEventListener('focusin', e => { const r = e.target.closest('.boat'); if (r) activate(+r.dataset.i); });
    if (LIVE) fetch('/api/boats').then(r => (r.ok ? r.json() : null)).then(j => { if (j && Array.isArray(j.boats) && j.boats.length) render(j.boats); }).catch(() => { /* keep the built in list */ });
    onFrame.push(() => {
      const vh = innerHeight;
      const line = innerWidth < 1024 ? photo.getBoundingClientRect().bottom + 48 : vh * 0.5;
      let best = -1, bd = Infinity;
      rows.forEach((r, i) => {
        const b = r.getBoundingClientRect();
        if (b.bottom < 0 || b.top > vh) return;
        const d = Math.abs(b.top + b.height / 2 - line);
        if (d < bd) { bd = d; best = i; }
      });
      if (best > -1) activate(best);
    });
  }

  /* ---------- Step-through forms: one question at a time ---------- */
  const num = v => {
    const t = String(v).trim().replace(/\s*(ft|feet|')\s*$/i, '');
    if (!t) return null;
    if (!/^\d{1,3}(\.\d)?$/.test(t)) return NaN;
    return parseFloat(t);
  };
  const feet = n => (Number.isInteger(n) ? String(n) : n.toFixed(1)) + ' ft';

  function flow(dlg, cfg) {
    const form = $('form', dlg);
    const steps = $$('.step', form);
    const bar = $('.val-bar span', dlg);
    let cur = 0;
    const setOut = (k, v) => $$(`[data-out="${k}"]`, dlg).forEach(n => {
      if (n.textContent !== v) { n.textContent = v; n.classList.remove('flash'); void n.offsetWidth; n.classList.add('flash'); }
    });
    function show(i, dir = 1) {
      steps[cur].hidden = true;
      cur = Math.max(0, Math.min(i, steps.length - 1));
      const s = steps[cur];
      s.hidden = false;
      s.classList.remove('enter', 'enter-back');
      void s.offsetWidth; s.classList.add(dir > 0 ? 'enter' : 'enter-back');
      bar.style.setProperty('--p', Math.max(0.05, Math.min(1, (cur + 1) / (steps.length - 1))));
      const field = s.querySelector('input:not([type="radio"]):not([type="checkbox"]), textarea');
      (field || s.querySelector('.q')).focus({ preventScroll: true });
    }
    function err(id, msg, fields) {
      const p = $('#' + id, dlg);
      p.textContent = msg; p.hidden = !msg;
      $$('input, textarea', p.closest('.step')).forEach(i => i.removeAttribute('aria-invalid'));
      (fields || []).forEach(f => f.setAttribute('aria-invalid', 'true'));
      if (fields && fields[0]) fields[0].focus();
      return false;
    }
    form.addEventListener('input', e => {
      const t = e.target;
      if (t.getAttribute('aria-invalid') !== 'true') return;
      t.removeAttribute('aria-invalid');
      const p = $('.err', t.closest('.step'));
      if (p) { p.hidden = true; p.textContent = ''; }
    });
    $$('[data-close]', dlg).forEach(b => b.addEventListener('click', () => dlg.close()));
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
    dlg.addEventListener('close', () => {
      document.documentElement.style.overflow = '';
      if (location.hash === '#' + dlg.id) history.replaceState(null, '', location.pathname + location.search);
    });
    form.addEventListener('change', e => {
      const t = e.target;
      if (t.type !== 'radio') return;
      const label = t.closest('label').querySelector('span').textContent;
      if (t.closest('[data-stay]')) { setOut(t.name, label); return; }
      setOut(t.name, t.value);
      setTimeout(() => show(cur + 1), reduce ? 0 : 260);
    });
    $$('[data-back]', form).forEach(b => b.addEventListener('click', () => show(cur - 1, -1)));
    $$('[data-next]', form).forEach(b => {
      const step = b.closest('.step');
      const go = () => { if (cfg.check[step.dataset.step]()) show(cur + 1); };
      b.addEventListener('click', go);
      $$('input', step).forEach(i => i.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); go(); } }));
    });
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const p = cfg.prefix;
      const name = $(`#${p}-name`), email = $(`#${p}-email`), phone = $(`#${p}-phone`), consent = $(`#${p}-consent`);
      const how = $('input[name="reply_by"]:checked', form);
      const eid = `${p}-e-contact`;
      const em = email.value.trim(), digits = phone.value.replace(/\D/g, '');
      if (!name.value.trim()) return err(eid, 'Add your name so I know who to reply to.', [name]);
      if (!em && !phone.value.trim()) return err(eid, 'Add an email address or a phone number so I can reach you.', [email]);
      if (em && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)) return err(eid, 'Check the email address. It should look like name@example.com.', [email]);
      if (phone.value.trim() && digits.length < 10) return err(eid, 'Add the phone number with its area code, for example 250 555 0182.', [phone]);
      if (how && how.value === 'email' && !em) return err(eid, 'Add your email address, or choose a call or a text instead.', [email]);
      if (how && how.value !== 'email' && !digits) return err(eid, 'Add a phone number so I can call or text you.', [phone]);
      if (!consent.checked) return err(eid, 'Tick the box so I’m allowed to reply to you.', [consent]);
      err(eid, '');
      const btn = $('[data-step="contact"] button[type="submit"]', form);
      stamp(form, cfg.subject());
      busy(btn, true);
      try { await send(form, cfg.files ? await cfg.files() : null); }
      catch (x) { busy(btn, false); return err(eid, FAIL, []); }
      busy(btn, false);
      setOut('first', name.value.trim().split(/\s+/)[0]);
      const v = how ? how.value : (em ? 'email' : 'call');
      setOut('next', cfg.next[v](em));
      show(steps.findIndex(s => s.dataset.step === 'done'));
    });
    return {
      open(reset) { if (!dlg.open) { dlg.showModal(); document.documentElement.style.overflow = 'hidden'; show(reset || cur === steps.length - 1 ? 0 : cur); } },
      err, setOut
    };
  }

  const flows = {};

  const vDlg = $('#value');
  if (vDlg) {
    const make = $('#v-make'), model = $('#v-model'), year = $('#v-year'), vlen = $('#v-len');
    let V;
    const vTitle = () => V.setOut('title', [year.value.trim(), make.value.trim(), model.value.trim()].filter(Boolean).join(' ') || 'Not named yet');
    let photos = [];
    const shrink = async file => {
      try {
        const bmp = await createImageBitmap(file);
        const k = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
        const c = document.createElement('canvas');
        c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
        c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
        const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.82));
        if (blob) return blob;
      } catch (e) { /* the browser can't read this photo; fall back to the original if it's small */ }
      return file.size <= 2.5 * 1024 * 1024 ? file : null;
    };
    V = flow(vDlg, {
      prefix: 'v',
      subject: () => {
        const t = [year.value.trim(), make.value.trim(), model.value.trim()].filter(Boolean).join(' ') || 'a boat';
        const n = num(vlen.value);
        return `Valuation request: ${t}${n && n >= 8 ? ', ' + feet(n) : ''}`;
      },
      files: async () => (await Promise.all(photos.slice(0, 3).map(shrink))).filter(Boolean),
      check: {
        model() {
          const y = year.value.trim(), maxY = new Date().getFullYear() + 1;
          if (!make.value.trim()) return V.err('v-e-model', 'Add the make, for example Grand Banks or Beneteau.', [make]);
          if (y && (!/^\d{4}$/.test(y) || +y < 1900 || +y > maxY)) return V.err('v-e-model', `Enter the year as four digits, between 1900 and ${maxY}.`, [year]);
          V.err('v-e-model', ''); vTitle(); return true;
        },
        length() {
          const n = num(vlen.value);
          if (n === null) return V.err('v-e-len', 'Enter her length in feet, for example 34.', [vlen]);
          if (Number.isNaN(n) || n < 8 || n > 200) return V.err('v-e-len', 'Enter a length in feet between 8 and 200, for example 34 or 34.5.', [vlen]);
          V.err('v-e-len', ''); V.setOut('length', feet(n)); return true;
        }
      },
      next: {
        email: e => `email your written valuation to ${e}`,
        call: () => 'call you first so we can talk it through',
        text: () => 'text you to find a good time to talk'
      }
    });
    [make, model, year].forEach(i => i.addEventListener('input', vTitle));
    year.addEventListener('input', () => { year.value = year.value.replace(/\D/g, '').slice(0, 4); });
    vlen.addEventListener('input', () => { const n = num(vlen.value); if (n && n >= 8 && n <= 200) V.setOut('length', feet(n)); });
    const photoIn = $('#v-photo'), thumbs = $('[data-thumbs]', vDlg), vcPhoto = $('[data-vc-photo]', vDlg);
    if (photoIn) photoIn.addEventListener('change', () => {
      const files = [...photoIn.files];
      const bad = files.find(f => !/^image\//.test(f.type));
      const big = files.find(f => f.size > 15 * 1024 * 1024);
      if (bad) { photoIn.value = ''; return V.err('v-e-photo', 'That file isn’t a photo. Choose a JPG, PNG or HEIC image.', []); }
      if (big) { photoIn.value = ''; return V.err('v-e-photo', 'That photo is over 15 MB. Try a smaller copy.', []); }
      if (files.length > 3) { photoIn.value = ''; return V.err('v-e-photo', 'Add up to three photos.', []); }
      photos = files;
      $('#v-e-photo').hidden = true;
      thumbs.innerHTML = '';
      files.forEach(f => { const li = document.createElement('li'); const im = document.createElement('img'); im.src = URL.createObjectURL(f); im.alt = ''; li.appendChild(im); thumbs.appendChild(li); });
      if (files[0]) { $('img', vcPhoto).src = URL.createObjectURL(files[0]); vcPhoto.hidden = false; } else vcPhoto.hidden = true;
    });
    flows.value = V;
  }

  const fDlg = $('#find');
  if (fDlg) {
    const from = $('#f-from'), to = $('#f-to');
    let F;
    const sizeText = (a, b) => (a && b ? `${a} to ${feet(b)}` : a ? `${feet(a)} and up` : `Up to ${feet(b)}`);
    F = flow(fDlg, {
      prefix: 'f',
      subject: () => {
        const want = ($('input[name="want"]:checked', fDlg) || {}).value || 'a boat';
        const size = $('[data-out="size"]', fDlg).textContent;
        return `Boat search: ${want}${/ft/.test(size) ? ', ' + size : ''}`;
      },
      check: {
        size() {
          const a = num(from.value), b = num(to.value);
          if (a === null && b === null) return F.err('f-e-size', 'Enter at least one length in feet, for example 36.', [from]);
          for (const [n, el] of [[a, from], [b, to]]) {
            if (n !== null && (Number.isNaN(n) || n < 8 || n > 200)) return F.err('f-e-size', 'Enter lengths in feet between 8 and 200, for example 36.', [el]);
          }
          if (a !== null && b !== null && a > b) return F.err('f-e-size', 'The first length should be the shorter one.', [from]);
          F.err('f-e-size', ''); F.setOut('size', sizeText(a, b)); return true;
        }
      },
      next: {
        email: e => `email boats that fit to ${e}`,
        call: () => 'call you first so we can talk it through',
        text: () => 'text you to find a good time to talk'
      }
    });
    flows.find = F;
  }

  const aDlg = $('#ask');
  if (aDlg) {
    let asking = 'this boat';
    const A = flow(aDlg, {
      prefix: 'a', check: {},
      subject: () => `Question about the ${asking}`,
      next: { email: e => `email you at ${e}`, call: () => 'call you', text: () => 'text you' }
    });
    document.addEventListener('click', e => {
      const b = e.target.closest('[data-ask]');
      if (!b) return;
      const name = b.dataset.ask;
      asking = name;
      A.setOut('boat', name);
      A.setOut('price', b.dataset.price);
      const f = $('form', aDlg);
      f.elements.boat.value = name;
      f.elements.asking_price.value = b.dataset.price || '';
      f.elements.listing_url.value = b.dataset.url || '';
      $('#a-msg').value = `I’d like to know more about the ${name}. Is she still available?`;
      A.open(true);
    });
  }

  /* ---------- Market notes ---------- */
  const notes = $('#notes');
  if (notes) notes.addEventListener('submit', async e => {
    e.preventDefault();
    const email = $('#n-email'), consent = $('#n-consent'), er = $('#n-err'), ok = $('#n-ok');
    const fail = (msg, el) => { er.textContent = msg; er.hidden = false; ok.hidden = true; el.setAttribute('aria-invalid', 'true'); el.focus(); };
    email.removeAttribute('aria-invalid'); consent.removeAttribute('aria-invalid');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) return fail('Check the email address. It should look like name@example.com.', email);
    if (!consent.checked) return fail('Tick the box so I’m allowed to send them to you.', consent);
    er.hidden = true;
    const boat = notes.elements.boat.value.trim();
    stamp(notes, `Market notes signup${boat ? ': ' + boat : ''}`);
    const btn = $('button[type="submit"]', notes);
    busy(btn, true);
    try { await send(notes); }
    catch (x) { busy(btn, false); er.textContent = FAIL; er.hidden = false; return; }
    busy(btn, false);
    ok.hidden = false; ok.focus();
  });

  /* ---------- Open the forms from buttons and from links like #value ---------- */
  $$('[data-open]').forEach(a => a.addEventListener('click', e => {
    const f = flows[a.dataset.open];
    if (!f) return;
    e.preventDefault();
    setMenu(false);
    f.open();
  }));
  function route() { const f = flows[location.hash.slice(1)]; if (f) f.open(); }
  route();
  addEventListener('hashchange', route);
  kick();
})();
