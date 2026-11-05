// Servings stepper: rescales ingredient amounts that carry data-qty.
(function () {
  var list = document.getElementById('ingredient-list');
  var out = document.getElementById('serves');
  if (!list || !out) return;
  var base = Number(list.getAttribute('data-base-serves')) || 1;
  var serves = base;
  var FRACTIONS = { 0.25: '¼', 0.5: '½', 0.75: '¾' };

  function format(n) {
    var whole = Math.floor(n);
    var frac = Math.round((n - whole) * 4) / 4;
    if (frac === 1) { whole += 1; frac = 0; }
    var f = FRACTIONS[frac] || '';
    if (whole === 0) return f || '0';
    return whole + (f ? ' ' + f : '');
  }

  function render() {
    out.textContent = serves + (serves === 1 ? ' serving' : ' servings');
    var items = list.querySelectorAll('[data-qty]');
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      var qty = Number(el.getAttribute('data-qty')) * serves / base;
      el.textContent = format(qty) + ' ' + el.getAttribute('data-unit');
    }
  }

  document.querySelectorAll('.servings button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      serves = Math.min(12, Math.max(1, serves + Number(btn.getAttribute('data-step'))));
      render();
    });
  });
})();
