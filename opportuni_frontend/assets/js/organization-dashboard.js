// Organization Dashboard Controller
(function(){
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  function mountNavbar(){ try { window.OrgNavbar?.mount?.(); } catch(e){ console.error(e); } }

  function showLoader(on){ try { window.Components?.showLoading?.(!!on); } catch{} }

  function formatCount(v){
    const n = Number(v||0);
    if (n >= 1000) return (n/1000).toFixed(n%1000?1:0)+'k';
    return String(n);
  }

  async function loadKPIs(){
    try {
      const stats = await window.api.organizations.getDashboardStats();
      $('#kpiActive').textContent = formatCount(stats.active_opportunities || stats.active_count || 0);
      $('#kpiNewApps').textContent = formatCount(stats.new_applications || stats.applications_today || 0);
      $('#kpiInterviews').textContent = formatCount(stats.interviews_scheduled || stats.interviews || 0);
      $('#kpiHires').textContent = formatCount(stats.hires_month || stats.hires || 0);
    } catch(err){ console.warn('KPI load failed', err); }
  }

  function liRecent(app){
    const name = [app.student_first_name, app.student_last_name].filter(Boolean).join(' ') || app.student_name || 'Applicant';
    const role = app.opportunity_title || 'Opportunity';
    const status = app.status || 'new';
    return `<li class="list-item">
      <div class="list-item__left">
        <img class="avatar" src="${Utils.escapeHTML(app.student_avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(name))}" alt="${Utils.escapeHTML(name)}">
        <div class="meta">
          <span class="meta__title">${Utils.escapeHTML(name)}</span>
          <span class="meta__sub">${Utils.escapeHTML(role)}</span>
        </div>
      </div>
      <span class="badge ${status==='new'?'badge--new':''}">${Utils.escapeHTML(status)}</span>
    </li>`;
  }

  async function loadRecentApplications(){
    const host = $('#recentApps');
    if(!host) return;
    host.setAttribute('aria-busy','true');
    try {
  const data = await window.api.organizations.getApplications({ ordering: '-applied_at', page_size: 6 });
      const items = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : []);
      if(!items.length){ $('#recentAppsEmpty').classList.remove('hidden'); return; }
      host.innerHTML = items.map(liRecent).join('');
    } catch(err){ console.warn('Recent applications failed', err); $('#recentAppsEmpty').classList.remove('hidden'); }
    finally { host.removeAttribute('aria-busy'); }
  }

  function liOpp(o){
    const title = o.title || 'Untitled';
    const apps = Number(o.applications_count || 0);
    return `<li class="list-item">
      <div class="meta">
        <span class="meta__title">${Utils.escapeHTML(title)}</span>
        <span class="meta__sub">${apps} application${apps===1?'':'s'}</span>
      </div>
      <a class="panel__link" href="/organization/applications.html?opportunity=${encodeURIComponent(o.id)}">Open</a>
    </li>`;
  }

  async function loadActiveOpportunities(){
    const host = $('#activeOpps');
    if(!host) return;
    host.setAttribute('aria-busy','true');
    try {
      const list = await window.api.organizations.getOpportunities({ is_active: true, ordering: '-created_at', page_size: 6 });
      const items = Array.isArray(list?.results) ? list.results : (Array.isArray(list) ? list : []);
      if(!items.length){ $('#activeOppsEmpty').classList.remove('hidden'); return; }
      host.innerHTML = items.map(liOpp).join('');
    } catch(err){ console.warn('Active opps failed', err); $('#activeOppsEmpty').classList.remove('hidden'); }
    finally { host.removeAttribute('aria-busy'); }
  }

  async function loadActivity(){
    const host = $('#activity'); if(!host) return;
    // Placeholder until notifications/activity endpoint mapped
    const demo = [];
    if(!demo.length) $('#activityEmpty').classList.remove('hidden');
  }

  // Modal controls
  function openCreate(){ const m = $('#modalCreate'); if(!m) return; m.classList.remove('hidden'); document.body.classList.add('no-scroll'); }
  function closeCreate(){ const m = $('#modalCreate'); if(!m) return; m.classList.add('hidden'); document.body.classList.remove('no-scroll'); }
  function bindModal(){
    // Only bind modal handlers if the inline modal exists on this page (legacy fallback)
    const modal = $('#modalCreate');
    if(!modal) return; // New flow uses dedicated create page via anchor link
    const btn = $('#btnCreate');
    btn?.addEventListener('click', (e)=>{ e.preventDefault(); openCreate(); });
    $$('#modalCreate [data-close]').forEach(el=> el.addEventListener('click', closeCreate));
    $('#modalCreate .modal__backdrop')?.addEventListener('click', closeCreate);
    document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeCreate(); });
  }

  async function submitCreate(e){
    e.preventDefault();
    const form = e.currentTarget;
    const data = Utils.getFormData(form);
    try {
      showLoader(true);
      await window.api.opportunities.create(data);
      window.Components?.showToast?.('Opportunity created', 'success');
      closeCreate();
      form.reset();
      await Promise.all([loadActiveOpportunities(), loadKPIs()]);
    } catch(err){
      window.Components?.showToast?.(err.message || 'Failed to create opportunity', 'error');
    } finally { showLoader(false); }
  }

  function bind(){ $('#formCreate')?.addEventListener('submit', submitCreate); }

  async function init(){
    mountNavbar();
    bindModal();
    bind();
    await Promise.all([loadKPIs(), loadRecentApplications(), loadActiveOpportunities(), loadActivity()]);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
