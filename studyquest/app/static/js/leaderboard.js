(function () {
  const input = document.getElementById('user-search');
  const out   = document.getElementById('search-results');
  if (!input) return;
  const url   = input.dataset.searchUrl;
  let timer = null;
  let activeReq = 0;

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function render(results) {
    out.style.display = 'block';
    if (!results.length) {
      out.innerHTML =
        '<div class="search-no-results">No scholars match.</div>';
      return;
    }
    out.innerHTML = results.map(r =>
      '<a href="' + r.url + '" class="leaderboard-row search-result-row">' +
        '<div class="leaderboard-avatar">' + r.emoji + '</div>' +
        '<div class="leaderboard-user-info">' +
          '<div class="leaderboard-username">' + escapeHtml(r.username) + '</div>' +
          '<div class="leaderboard-user-meta">' + escapeHtml(r.title) + ' · Level ' + r.level + '</div>' +
        '</div>' +
        '<span class="badge badge-level badge-spaced-right">Lv ' + r.level + '</span>' +
        '<div class="leaderboard-xp">' + r.xp + '</div>' +
      '</a>'
    ).join('');
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    const q = this.value.trim();
    if (!q) {
      out.style.display = 'none';
      out.innerHTML = '';
      return;
    }
    const myReq = ++activeReq;
    timer = setTimeout(function () {
      fetch(url + '?q=' + encodeURIComponent(q), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(r => r.json())
        .then(data => { if (myReq === activeReq) render(data.results || []); })
        .catch(() => {
          if (myReq === activeReq) {
            out.style.display = 'block';
            out.innerHTML =
              '<div class="search-error">Search failed. Try again.</div>';
          }
        });
    }, 200);
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      this.value = '';
      out.style.display = 'none';
      out.innerHTML = '';
    }
  });
})();
