/**
 * main.js — NexStore global JavaScript
 * Handles: dark/light mode, live search, cart AJAX,
 *          wishlist AJAX, toast auto-dismiss, user menu,
 *          mobile nav, add-to-cart forms.
 */

/* ── Theme ─────────────────────────────────────────────────── */
(function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
})();

function updateThemeIcon(theme) {
  const icon = document.querySelector('.theme-icon');
  if (icon) icon.textContent = theme === 'dark' ? '🌙' : '☀️';
}

document.getElementById('themeToggle')?.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcon(next);
});

/* ── Toast Notifications ───────────────────────────────────── */
function showToast(message, type = 'info', duration = 4000) {
  const icons = { success: '✅', danger: '❌', warning: '⚠️', info: 'ℹ️' };
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
    <span class="toast-msg">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

/* Auto-dismiss server-rendered toasts */
document.querySelectorAll('.toast.show').forEach(toast => {
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4000);
});

/* ── User Dropdown ─────────────────────────────────────────── */
const userMenuBtn = document.getElementById('userMenuBtn');
const userDropdown = document.getElementById('userDropdown');
userMenuBtn?.addEventListener('click', e => {
  e.stopPropagation();
  userDropdown?.classList.toggle('show');
});
document.addEventListener('click', () => userDropdown?.classList.remove('show'));

/* ── Mobile Nav ────────────────────────────────────────────── */
document.getElementById('hamburger')?.addEventListener('click', () => {
  document.getElementById('mobileNav')?.classList.toggle('open');
});

/* ── Live Search ───────────────────────────────────────────── */
let searchTimer = null;
const searchInput = document.getElementById('searchInput');
const searchDropdown = document.getElementById('searchDropdown');

searchInput?.addEventListener('input', function () {
  const q = this.value.trim();
  clearTimeout(searchTimer);
  if (q.length < 2) { searchDropdown.classList.remove('show'); return; }
  searchTimer = setTimeout(() => fetchSearch(q), 280);
});

searchInput?.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') searchDropdown.classList.remove('show');
});

document.addEventListener('click', e => {
  if (!document.getElementById('searchWrapper')?.contains(e.target)) {
    searchDropdown?.classList.remove('show');
  }
});

function fetchSearch(q) {
  fetch(`/api/search?q=${encodeURIComponent(q)}`)
    .then(r => r.json())
    .then(data => {
      if (!data.length) { searchDropdown.classList.remove('show'); return; }
      searchDropdown.innerHTML = data.map(p => `
        <a href="/product/${p.id}" class="search-result-item">
          <img src="${p.image_url}" alt="${p.name}" loading="lazy"/>
          <div class="search-result-info">
            <div class="name">${p.name}</div>
            <div class="cat">${p.category}</div>
            <div class="price">$${p.price.toFixed(2)}</div>
          </div>
        </a>`).join('');
      searchDropdown.classList.add('show');
    })
    .catch(() => {});
}

/* ── Add to Cart (AJAX) ────────────────────────────────────── */
document.addEventListener('submit', function (e) {
  const form = e.target;
  const isCardForm = form.classList.contains('add-cart-form');
  const isDetailForm = form.classList.contains('add-to-cart-form');

  if (!isCardForm && !isDetailForm) return;

  e.preventDefault();

  const productId = form.querySelector('[name="product_id"]').value;
  const qtyInput = form.querySelector('[name="quantity"]');
  const quantity = qtyInput ? qtyInput.value : 1;

  const btn = form.querySelector('button[type="submit"]');
  if (!btn) return;

  const orig = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '⏳ Adding…';

  fetch('/cart/add', {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: `product_id=${productId}&quantity=${quantity}`
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      updateCartBadge(data.cart_count);
      btn.innerHTML = '✅ Added!';
      setTimeout(() => {
        btn.innerHTML = orig;
        btn.disabled = false;
      }, 1800);
    } else {
      showToast(data.message || 'Failed to add to cart', 'danger');
      btn.innerHTML = orig;
      btn.disabled = false;
    }
  })
  .catch(() => {
    showToast('Network error. Please try again.', 'danger');
    btn.innerHTML = orig;
    btn.disabled = false;
  });
});

/* ── Wishlist Toggle ───────────────────────────────────────── */
document.addEventListener('click', function (e) {
  const btn = e.target.closest('.wishlist-btn');
  if (!btn) return;
  const productId = btn.dataset.productId;
  if (!productId) return;

  fetch('/wishlist/toggle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `product_id=${productId}`
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      const added = data.action === 'added';
      btn.classList.toggle('wishlisted', added);
      btn.textContent = added ? '💛' : '❤️';
      showToast(added ? 'Added to wishlist! 💛' : 'Removed from wishlist', added ? 'success' : 'info');
    } else {
      showToast('Please log in to use the wishlist.', 'warning');
      setTimeout(() => window.location.href = '/auth/login', 1200);
    }
  })
  .catch(() => showToast('Network error.', 'danger'));
});

/* ── Cart Badge ────────────────────────────────────────────── */
function updateCartBadge(count) {
  const badge = document.getElementById('cartBadge');
  if (!badge) return;
  badge.textContent = count;
  badge.style.transform = 'scale(1.5)';
  setTimeout(() => badge.style.transform = 'scale(1)', 300);
}

/* ── Detail page wishlist btn text update ─────────────────── */
const wishlistBtn = document.getElementById('wishlistBtn');
if (wishlistBtn) {
  wishlistBtn.addEventListener('click', function () {
    const isWishlisted = this.classList.contains('wishlisted');
    this.textContent = isWishlisted ? '💛 Remove from Wishlist' : '❤️ Add to Wishlist';
  });
}
