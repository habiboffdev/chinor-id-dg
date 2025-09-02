// Universal Organization Navbar (no Tailwind)
// Usage: include theme.css and this file, then add <div id="org-navbar"></div> in body top; call OrgNavbar.mount()

(function(){
  const html = () => `
    <nav class="org-nav" role="navigation" aria-label="Organization navigation">
      <div class="org-nav__inner">
        <a href="dashboard.html" class="org-nav__brand brand-wordmark">
          <i class="fas fa-bolt brand__icon"></i>Opportuni <span style="color: var(--accent-2);">org</span>
        </a>
        <ul class="org-nav__links" role="menubar">
          ${link('dashboard.html','<i class="fas fa-chart-line"></i> Dashboard')}
          ${link('opportunities.html','<i class="fas fa-briefcase"></i> Opportunities')}
          ${link('applications.html','<i class="fas fa-file-alt"></i> Applications')}
          ${link('students.html','<i class="fas fa-users"></i> Students')}
          ${link('communications.html','<i class="fas fa-comments"></i> Communications')}
          ${link('profile.html','<i class="fas fa-user"></i> Profile')}
        </ul>
        <div class="org-nav__actions">
          <button class="org-nav__bell" id="org-nav-bell" aria-label="Notifications">
            <i class="fas fa-bell" aria-hidden="true"></i>
            <span class="bell__badge" id="org-nav-badge" hidden>0</span>
          </button>
          <div class="org-nav__user">
            <button class="user__btn" id="org-user-btn" aria-haspopup="true" aria-expanded="false">
              <img class="user__avatar user-avatar" alt="Avatar" />
              <span class="user__name user-name">—</span>
              <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
            <div class="user__menu" id="org-user-menu" role="menu" hidden>
              <a role="menuitem" href="profile.html"><i class="fas fa-user"></i> Profile</a>
              <a role="menuitem" href="../settings.html"><i class="fas fa-cog"></i> Settings</a>
              <hr style="border: none; height: 1px; background: var(--slate-400); margin: 4px 0;">
              <button role="menuitem" id="org-logout"><i class="fas fa-sign-out-alt"></i> Sign out</button>
            </div>
          </div>
        </div>
      </div>
    </nav>`;

  function link(href, label){
    const active = (typeof window !== 'undefined') && window.location && 
      (window.location.pathname.endsWith(href) || 
       (href.includes('opportunities') && window.location.pathname.includes('opportunity-create')));
    return `<li role="none"><a role="menuitem" class="org-link${active? ' is-active':''}" ${active? 'aria-current="page"':''} href="${href}">${label}</a></li>`;
  }

  function mount(){
    const host = document.getElementById('org-navbar');
    if(!host) return;
    host.innerHTML = html();
    hydrate();
  }

  function hydrate(){
    // Update user info via auth.js if available
    try {
      const cur = window.auth?.getCurrentUser?.();
      if(cur){
        const nameEls = document.querySelectorAll('.user-name');
        nameEls.forEach(el=> el.textContent = `${cur.first_name || ''} ${cur.last_name || ''}`.trim() || cur.email || 'User');
        const avatarEls = document.querySelectorAll('.user-avatar');
        const src = cur.avatar || (window.auth?.generateAvatarURL?.(cur.first_name, cur.last_name));
        avatarEls.forEach(img=> { img.src = src; img.width=28; img.height=28; });
      }
    } catch {}

    // Dropdown toggling
    const btn = document.getElementById('org-user-btn');
    const menu = document.getElementById('org-user-menu');
    const logout = document.getElementById('org-logout');

    function openMenu(){
      if(!menu) return;
      menu.classList.remove('is-closed');
      menu.removeAttribute('hidden');
      btn?.setAttribute('aria-expanded','true');
      // trap first focusable for convenience
      setTimeout(()=> menu.querySelector('a,button,input,select,textarea')?.focus(), 0);
    }
  function closeMenu(){
      if(!menu) return;
      if(!menu.hasAttribute('hidden')){
    menu.setAttribute('hidden','');
    menu.classList.add('is-closed');
        btn?.setAttribute('aria-expanded','false');
      }
    }
    function toggleMenu(){
      if(menu?.hasAttribute('hidden')) openMenu(); else closeMenu();
    }
    if(btn && menu){
      // Primary toggle
      btn.addEventListener('click', (e)=>{ e.stopPropagation(); toggleMenu(); });
      // Close on outside pointer/click
      const outside = (e)=>{ if(!menu.contains(e.target) && !btn.contains(e.target)) closeMenu(); };
      document.addEventListener('pointerdown', outside, true);
      document.addEventListener('click', outside, true);
      // Close on focus leaving menu/button
      document.addEventListener('focusin', (e)=>{ if(!menu.contains(e.target) && !btn.contains(e.target)) closeMenu(); });
      // Keyboard ESC
      document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') { closeMenu(); btn.focus(); } });
      // Close on scroll/resize/navigation
      window.addEventListener('scroll', closeMenu, { passive: true });
      window.addEventListener('resize', closeMenu);
      window.addEventListener('popstate', closeMenu);
      // Close when any menu item is activated
      menu.addEventListener('click', (e)=>{
        const t = e.target;
        if(t && (t.tagName === 'A' || t.tagName === 'BUTTON')) closeMenu();
      });
    }
    if(logout){ logout.addEventListener('click', ()=> window.auth?.logout?.()); }

    // Notifications
    const badge = document.getElementById('org-nav-badge');
    try { window.api?.notifications?.getUnreadCount?.().then(r=>{
      const n = (r && (r.count || r.unread || r.total || r)) || 0;
      if(Number(n) > 0){ badge.textContent = String(n); badge.removeAttribute('hidden'); }
    }).catch(()=>{}); } catch {}

    // Scroll effect
    const nav = document.querySelector('.org-nav');
    const onScroll = ()=>{
      if(window.scrollY > 12) nav.classList.add('navbar--scrolled'); else nav.classList.remove('navbar--scrolled');
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  window.OrgNavbar = { mount };
})();
