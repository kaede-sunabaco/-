(() => {
  const header = document.querySelector('.site-header');
  if (!header) return;

  const button = header.querySelector('.menu-button');
  const menu = header.querySelector('.global-nav');
  if (!button || !menu) return;

  if (!menu.id) menu.id = 'global-menu';
  button.setAttribute('aria-controls', menu.id);
  button.setAttribute('aria-expanded', 'false');

  const closeMenu = () => {
    header.classList.remove('is-menu-open');
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-label', 'メニューを開く');
  };

  button.addEventListener('click', () => {
    const isOpen = header.classList.toggle('is-menu-open');
    button.setAttribute('aria-expanded', String(isOpen));
    button.setAttribute('aria-label', isOpen ? 'メニューを閉じる' : 'メニューを開く');
  });

  menu.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });

  document.addEventListener('click', (event) => {
    if (!header.contains(event.target)) closeMenu();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) closeMenu();
  });
})();
