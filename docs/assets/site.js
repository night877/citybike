(function () {
  var PHONE = '79137585571', TG = 'mr_org54', KEY = 'citybike_picks';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var money = function (n) { return Number(n).toLocaleString('ru-RU') + ' ₽'; };
  var wa = function (t) { return 'https://wa.me/' + PHONE + '?text=' + encodeURIComponent(t); };
  var tg = function (t) { return 'https://t.me/' + TG + '?text=' + encodeURIComponent(t); };

  var burger = $('.burger'), nav = $('.nav');
  if (burger) burger.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  });

  // Search over visible rows, used by the price lists and the catalog.
  function norm(s) { return (s || '').toLowerCase().replace(/ё/g, 'е'); }

  var priceInput = $('#price-q');
  if (priceInput) priceInput.addEventListener('input', function () {
    var q = norm(priceInput.value.trim()), any = false;
    $$('details.pl').forEach(function (d) {
      var hit = false;
      $$('.pl-rows div', d).forEach(function (r) {
        var ok = !q || norm(r.textContent).indexOf(q) > -1;
        r.hidden = !ok;
        hit = hit || ok;
      });
      d.hidden = !hit;
      if (q) d.open = hit; else d.open = false;
      any = any || hit;
    });
    $('#price-empty').style.display = any ? 'none' : 'block';
  });

  var diagInput = $('#diag-q');
  if (diagInput) {
    var diagCat = 'all';
    var applyDiag = function () {
      var q = norm(diagInput.value.trim()), any = false;
      $$('.diag').forEach(function (c) {
        var ok = (diagCat === 'all' || c.dataset.cat === diagCat) && (!q || norm(c.textContent + ' ' + c.dataset.kw).indexOf(q) > -1);
        c.hidden = !ok;
        any = any || ok;
      });
      $('#diag-empty').style.display = any ? 'none' : 'block';
    };
    diagInput.addEventListener('input', applyDiag);
    $$('[data-diag]').forEach(function (b) {
      b.addEventListener('click', function () {
        diagCat = b.dataset.diag;
        $$('[data-diag]').forEach(function (x) { x.classList.toggle('on', x === b); });
        applyDiag();
      });
    });
  }

  var catInput = $('#cat-q');
  if (catInput) catInput.addEventListener('input', function () {
    var q = norm(catInput.value.trim()), any = false;
    $$('.card').forEach(function (c) {
      var ok = !q || norm(c.dataset.q).indexOf(q) > -1;
      c.hidden = !ok;
      any = any || ok;
    });
    $$('.cat-block').forEach(function (b) { b.hidden = !$$('.card:not([hidden])', b).length; });
    $('#cat-empty').style.display = any ? 'none' : 'block';
  });

  // Picks replace the cart: a list the visitor sends to the workshop as one message.
  var picks = [];
  try { picks = JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { picks = []; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(picks)); } catch (e) {} }
  var bar = $('.pick-bar'), pickDlg = $('#picks');

  function pickText() {
    var lines = picks.map(function (p, i) { return (i + 1) + '. ' + p.title + (p.price ? ' — ' + money(p.price) : ''); });
    return 'Здравствуйте! Хочу уточнить наличие и забронировать:\n' + lines.join('\n');
  }
  function renderPicks() {
    if (bar) {
      bar.classList.toggle('show', picks.length > 0);
      bar.textContent = 'Подборка: ' + picks.length;
    }
    $$('[data-pick]').forEach(function (b) {
      var on = picks.some(function (p) { return p.id === b.dataset.pick; });
      b.setAttribute('aria-pressed', on);
      b.textContent = on ? '✓ В подборке' : '+ В подборку';
    });
    if (!pickDlg) return;
    var list = $('#pick-list');
    list.textContent = '';
    picks.forEach(function (p) {
      var row = document.createElement('div');
      row.className = 'pick-row';
      var label = document.createElement('span');
      label.textContent = p.title + (p.price ? ' — ' + money(p.price) : '');
      var del = document.createElement('button');
      del.type = 'button';
      del.textContent = '×';
      del.setAttribute('aria-label', 'Убрать из подборки');
      del.addEventListener('click', function () {
        picks = picks.filter(function (x) { return x.id !== p.id; });
        save(); renderPicks();
        if (!picks.length) pickDlg.close();
      });
      row.appendChild(label);
      row.appendChild(del);
      list.appendChild(row);
    });
    var sum = picks.reduce(function (s, p) { return s + (p.price || 0); }, 0);
    $('#pick-sum').textContent = sum ? 'Ориентировочно: ' + money(sum) : '';
    $('#pick-wa').href = wa(pickText());
    $('#pick-tg').href = tg(pickText());
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-pick]');
    if (!b) return;
    var exists = picks.some(function (p) { return p.id === b.dataset.pick; });
    picks = exists ? picks.filter(function (p) { return p.id !== b.dataset.pick; })
      : picks.concat([{ id: b.dataset.pick, title: b.dataset.title, price: Number(b.dataset.price) || 0 }]);
    save(); renderPicks();
  });
  if (bar) bar.addEventListener('click', function () { pickDlg.showModal(); });
  var clear = $('#pick-clear');
  if (clear) clear.addEventListener('click', function () { picks = []; save(); renderPicks(); pickDlg.close(); });
  $$('.dlg-x').forEach(function (x) { x.addEventListener('click', function () { x.closest('dialog').close(); }); });
  $$('dialog').forEach(function (d) {
    d.addEventListener('click', function (e) { if (e.target === d) d.close(); });
  });

  // Product details
  var pd = $('#product');
  $$('[data-open]').forEach(function (b) {
    b.addEventListener('click', function () {
      var c = b.closest('.card');
      var g = $('.dlg-gal', pd);
      g.textContent = '';
      (c.dataset.imgs || '').split(',').filter(Boolean).forEach(function (src) {
        var i = new Image();
        i.src = src;
        i.alt = c.dataset.title;
        g.appendChild(i);
      });
      $('h2', pd).textContent = c.dataset.title;
      $('.dlg-text', pd).textContent = c.dataset.text || '';
      $('.dlg-price', pd).textContent = c.dataset.price ? money(c.dataset.price) : 'Цена по запросу';
      $('.dlg-stock', pd).textContent = c.dataset.stock;
      var msg = 'Здравствуйте! Интересует: ' + c.dataset.title + '. Есть в наличии?';
      $('.dlg-wa', pd).href = wa(msg);
      $('.dlg-tg', pd).href = tg(msg);
      pd.showModal();
    });
  });

  renderPicks();
})();
