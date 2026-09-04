document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-hub]').forEach(function (hub) {
    const search = hub.querySelector('input[type="search"]');
    const tabs = Array.from(hub.querySelectorAll('.hub-tab'));
    const items = Array.from(hub.querySelectorAll('.hub-item'));
    const empty = hub.querySelector('.hub-empty--filtered');
    let activeFilter = 'all';

    function applyFilters() {
      const term = (search ? search.value : '').trim().toLowerCase();
      let visible = 0;
      if (activeFilter === 'all' && !term) {
        const lists = new Set(items.map(function (item) { return item.parentElement; }));
        lists.forEach(function (list) {
          Array.from(list.querySelectorAll('.hub-item'))
            .sort(function (first, second) {
              return Number(first.dataset.paymentStatus === 'paid') - Number(second.dataset.paymentStatus === 'paid');
            })
            .forEach(function (item) { list.appendChild(item); });
        });
      }
      items.forEach(function (item) {
        const status = item.dataset.filterStatus || '';
        const paymentStatus = item.dataset.paymentStatus || '';
        const text = (item.dataset.search || item.textContent || '').toLowerCase();
        const statusMatch = activeFilter === 'all' || status === activeFilter || paymentStatus === activeFilter;
        const textMatch = !term || text.includes(term);
        const show = statusMatch && textMatch;
        item.hidden = !show;
        if (show) visible += 1;
      });
      if (empty) empty.hidden = visible !== 0;
    }

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        activeFilter = tab.dataset.filter || 'all';
        tabs.forEach(function (t) { t.classList.toggle('is-active', t === tab); });
        applyFilters();
      });
    });
    if (search) search.addEventListener('input', applyFilters);
    applyFilters();
  });
});
