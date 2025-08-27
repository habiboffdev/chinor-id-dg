// Student Navbar Component for Opportuni
// Fresh brand-forward navbar with a capsule link rail, animated active indicator,
// robust dropdowns, and solid dark UI (no gradients).

(function(){
  const NAV_ID = 'student-navbar-root';

  function html(strings, ...vals){
    return strings.reduce((acc, s, i) => acc + s + (vals[i] ?? ''), '');
  }

  function ensureStyles(){
    if(document.getElementById('student-nav-styles')) return;
    const style = document.createElement('style');
    style.id = 'student-nav-styles';
  style.textContent = `
      /* Root bar */
      .hidden{display:none!important}
  .student-nav{position:sticky;top:0;background:var(--ink-900);isolation:isolate;z-index:70;box-shadow: 0 1px 0 rgba(255,255,255,0.06)}
      .student-nav::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:var(--slate-400);z-index:0}
      .student-nav .nav-wrap{position:relative;z-index:1;max-width:1280px;margin:0 auto;padding:0 16px}
      @media (min-width:640px){ .student-nav .nav-wrap{ padding:0 24px } }
      @media (min-width:1024px){ .student-nav .nav-wrap{ padding:0 32px } }

      /* Core layout */
      .student-nav .nav-core{height:64px;display:flex;align-items:center;justify-content:space-between}
      .student-nav .left-block{display:flex;align-items:center;gap:14px}

      /* Brand */
      .student-nav .brand{font-family:var(--font-display);color:var(--accent-2);font-weight:700;letter-spacing:-0.015em;display:inline-flex;align-items:center;gap:10px}
      .student-nav .brand .dot{width:8px;height:8px;border-radius:50%;background:var(--accent-1);box-shadow:0 0 0 2px rgba(200,255,0,0.15)}

      /* Capsule link rail */
  .student-nav .link-rail{position:relative;display:flex;align-items:center;gap:6px;background:var(--ink-800);border:1px solid var(--slate-400);border-radius:999px;padding:4px;overflow:visible}
  .student-nav .active-indicator{position:absolute;top:4px;bottom:4px;left:4px;border-radius:999px;background:var(--slate-600);border:1px solid var(--slate-400);box-shadow:none;width:0;transform:translateX(0);transition:transform 200ms ease,width 200ms ease}
      .student-nav .nav-link{position:relative;display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:999px;color:var(--mist-300);font-weight:600;white-space:nowrap}
  .student-nav a{ text-decoration: none }
  .student-nav a:hover{ text-decoration: none }
  .student-nav .nav-link{ text-decoration: none }
  .student-nav .nav-link:hover{color:var(--white-0); text-decoration: none }
  .student-nav .nav-link.active{color:var(--white-0);text-shadow:none; text-decoration: none }
  .student-nav .nav-link:focus{ outline: none }
  .student-nav .nav-link:focus-visible{ outline: none; box-shadow: 0 0 0 2px var(--slate-400) }

  /* Right cluster */
  .student-nav .menu-right{display:flex;align-items:center;gap:12px}
  .student-nav .btn-icon{display:inline-flex;align-items:center;justify-content:center;gap:8px;color:var(--mist-300);border-radius:12px;padding:8px;background:transparent;border:1px solid var(--slate-400);cursor:pointer;position:relative}
  .student-nav .btn-icon i{font-size:1rem}
  .student-nav .btn-icon:hover{filter:brightness(1.08);background:var(--ink-800)}
  .student-nav .btn-icon i.fa-chevron-down{ margin-left: 6px }
  .student-nav #notification-count{position:absolute;top:-6px;right:-6px;color:#fff;font-size:12px;border-radius:999px;height:20px;width:20px;display:flex;align-items:center;justify-content:center}
  .student-nav .user-avatar{display:block;height:32px;width:32px;border-radius:999px;object-fit:cover}
  .student-nav .user-name{display:none}
  /* Hide user menu by default until auth initializes */
  .student-nav .user-menu{ display:none }
  @media (min-width:768px){ .student-nav .user-name{display:inline} }

      /* Dropdowns */
      .student-nav .dd-wrap{position:relative}
      .student-nav .dropdown{position:absolute;right:0;top:calc(100% + 8px);min-width:12rem;background:var(--ink-900);border:1px solid var(--slate-400);border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.35);z-index:80}
      .student-nav .dropdown.hidden{display:none}
      .student-nav .dropdown a,.student-nav .dropdown button{display:block;width:100%;text-align:left;padding:10px 14px;color:var(--mist-200)}
      .student-nav .dropdown a:hover,.student-nav .dropdown button:hover{background:var(--ink-800)}

      /* Mobile */
      .student-nav .hamburger{display:none;color:var(--mist-300)}
      .student-nav .mobile-panel{display:none;position:absolute;left:0;right:0;top:100%;background:var(--ink-900);border-bottom:1px solid var(--slate-400);z-index:75}
      .student-nav .mobile-panel a{display:block;padding:12px 16px;color:var(--mist-200)}
      .student-nav .mobile-panel a.active{color:var(--accent-2)}
      .student-nav.open .mobile-panel{display:block}

      @media (max-width: 768px){
        .student-nav .link-rail{display:none}
        .student-nav .hamburger{display:inline-flex}
      }
    `;
    document.head.appendChild(style);
  }

  function currentPath(){
    const p = window.location.pathname;
    return p.replace(/\/$/, '');
  }

  function isActive(href){
    const path = currentPath();
    return path.endsWith(href);
  }

  function render(){
    ensureStyles();
    const root = document.getElementById(NAV_ID);
    const host = root || document.body;

    const nav = document.createElement('nav');
    nav.className = 'student-nav shadow-lg';
    nav.innerHTML = html`
      <div class="nav-wrap max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="nav-core">
          <div class="left-block">
            <a href="/" class="brand text-xl" aria-label="Opportuni Home">
              <span>Opportuni</span>
              <span class="dot" aria-hidden="true"></span>
            </a>
            <button class="hamburger btn-icon p-2" aria-label="Toggle menu" aria-expanded="false"><i class="fas fa-bars"></i></button>
            <div class="link-rail">
              <span class="active-indicator"></span>
              <a href="/dashboard.html" class="nav-link ${isActive('/dashboard.html') ? 'active':''}"><i class="fas fa-table-cells-large"></i><span>Dashboard</span></a>
              <a href="/opportunities.html" class="nav-link ${isActive('/opportunities.html') ? 'active':''}"><i class="fas fa-compass"></i><span>Opportunities</span></a>
              <a href="/applications.html" class="nav-link ${isActive('/applications.html') ? 'active':''}"><i class="fas fa-folder-open"></i><span>My Applications</span></a>
              <a href="/profile.html" class="nav-link ${isActive('/profile.html') ? 'active':''}"><i class="fas fa-user-circle"></i><span>Profile</span></a>
            </div>
          </div>

          <div class="menu-right">
            <div class="dd-wrap">
              <button class="btn-icon p-2" data-action="toggle-notifications" aria-haspopup="true" aria-expanded="false">
                <i class="fas fa-bell text-xl"></i>
                <span id="notification-count" class="absolute -top-1 -right-1 text-white text-xs rounded-full h-5 w-5 hidden items-center justify-center" style="background: var(--promo);">0</span>
              </button>
              <div id="nav-notifications" class="dropdown hidden w-80">
                <div class="p-3" style="border-bottom:1px solid var(--slate-400)"><strong>Notifications</strong></div>
                <div class="max-h-96 overflow-y-auto"></div>
                <div class="p-3" style="border-top:1px solid var(--slate-400)"><a href="/notifications.html" style="color: var(--accent-3);">View all</a></div>
              </div>
            </div>

            <div class="dd-wrap user-menu">
              <button class="flex items-center gap-2 p-2 rounded-lg btn-icon" data-action="toggle-user" aria-haspopup="true" aria-expanded="false">
                <img class="user-avatar h-8 w-8 rounded-full" src="https://ui-avatars.com/api/?name=User&background=3b82f6&color=ffffff" alt="User Avatar">
                <span class="user-name hidden md:block">User</span>
                <i class="fas fa-chevron-down"></i>
              </button>
              <div id="nav-user" class="dropdown hidden w-48">
                <div class="py-1">
                  <a href="/profile.html"><i class="fas fa-user mr-2"></i>Profile</a>
                  <a href="/settings.html"><i class="fas fa-cog mr-2"></i>Settings</a>
                  <hr style="border-color: var(--slate-400)">
                  <button data-action="logout"><i class="fas fa-sign-out-alt mr-2"></i>Sign Out</button>
                </div>
              </div>
            </div>

            <div class="auth-buttons flex items-center gap-2">
              <a href="/login.html" class="btn btn--ghost">Sign in</a>
              <a href="/signup.html" class="btn btn--secondary btn--pill">Sign up</a>
            </div>
          </div>
        </div>

        <div class="mobile-panel">
          <a href="/dashboard.html" class="${isActive('/dashboard.html') ? 'active':''}">Dashboard</a>
          <a href="/opportunities.html" class="${isActive('/opportunities.html') ? 'active':''}">Opportunities</a>
          <a href="/applications.html" class="${isActive('/applications.html') ? 'active':''}">My Applications</a>
          <a href="/profile.html" class="${isActive('/profile.html') ? 'active':''}">Profile</a>
        </div>
      </div>
    `;

    if(root){
      root.replaceWith(nav);
    } else {
      document.body.insertBefore(nav, document.body.firstChild);
    }

  wire(nav);
  positionIndicator(nav);
  window.addEventListener('resize', ()=> positionIndicator(nav));
  window.addEventListener('load', ()=> positionIndicator(nav));
  setTimeout(()=> positionIndicator(nav), 250);
    tryUpdateAuthUI();
  }

  function wire(nav){
    const qs = (sel)=> nav.querySelector(sel);
  const ddUserBtn = nav.querySelector('[data-action="toggle-user"]');
  const ddNotifBtn = nav.querySelector('[data-action="toggle-notifications"]');
    const ddUser = qs('#nav-user');
    const ddNotif = qs('#nav-notifications');
    const logoutBtn = nav.querySelector('[data-action="logout"]');
    const hamburger = nav.querySelector('.hamburger');
  const mobilePanel = nav.querySelector('.mobile-panel');

    const closeAll = ()=>{
      ddUser?.classList.add('hidden');
      ddNotif?.classList.add('hidden');
      ddUserBtn?.setAttribute('aria-expanded','false');
      ddNotifBtn?.setAttribute('aria-expanded','false');
    };

    ddUserBtn?.addEventListener('click', (e)=>{
      e.stopPropagation();
      const isHidden = ddUser.classList.contains('hidden');
      closeAll();
      if(isHidden){ ddUser.classList.remove('hidden'); ddUserBtn.setAttribute('aria-expanded','true'); }
    });

    ddNotifBtn?.addEventListener('click', (e)=>{
      e.stopPropagation();
      const isHidden = ddNotif.classList.contains('hidden');
      closeAll();
      if(isHidden){ ddNotif.classList.remove('hidden'); ddNotifBtn.setAttribute('aria-expanded','true'); }
    });

    document.addEventListener('click', (e)=>{
      if(!nav.contains(e.target)) closeAll();
    });

    logoutBtn?.addEventListener('click', ()=> { if(window.auth) auth.logout(); });

    hamburger?.addEventListener('click', ()=>{
      if(!mobilePanel) return;
      const open = nav.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // Reposition indicator when clicking links (in case of SPA-like navigation later)
    nav.querySelectorAll('.nav-link').forEach(a=>{
      a.addEventListener('click', ()=> setTimeout(()=> positionIndicator(nav), 0));
    });
  }

  function positionIndicator(nav){
    const rail = nav.querySelector('.link-rail');
    const indicator = nav.querySelector('.active-indicator');
    if(!rail || !indicator) return;
    const active = nav.querySelector('.nav-link.active') || nav.querySelector('.nav-link');
    if(!active) return;
    const rRail = rail.getBoundingClientRect();
    const r = active.getBoundingClientRect();
    const x = r.left - rRail.left;
    indicator.style.width = `${Math.max(0, r.width)}px`;
    indicator.style.transform = `translateX(${Math.max(0, x)}px)`;
  }

  function tryUpdateAuthUI(){
    // Defer to auth manager to populate user-name/avatar across the page
    const updateLoggedIn = ()=> auth.updateUIForLoggedInUser();
    const updateLoggedOut = ()=> auth.updateUIForLoggedOutUser();
    if(window.auth){
      auth.waitForUser().then(()=>{
        if(auth.isLoggedIn()) updateLoggedIn(); else updateLoggedOut();
      }).catch(()=>{
        // On error assume logged out UI
        updateLoggedOut();
      });
      // Fallback after a short delay in case waitForUser didn't trigger
      setTimeout(()=>{
        if(auth.isLoggedIn()) updateLoggedIn(); else updateLoggedOut();
      }, 300);
    }
  }

  // Auto-render on DOM ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }

  // Expose manual rerender for debug
  window.renderStudentNavbar = render;
})();
