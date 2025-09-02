// Interactive step-by-step wizard for creating an opportunity
(function(){
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  const steps = [
    'title',
    'description',
    'type',
    'location',
    'dates',
    'eligibility',
    'benefits',
    'requirements',
    'questions',
    'review'
  ];

  let current = 0;
  let typeValue = 'internship';

  function mountNavbar(){ try{ window.OrgNavbar?.mount?.(); }catch(e){ console.error(e); } }

  function updateProgress(){ 
    $('#progress').textContent = String(current+1); 
    // Update progress as fraction
    const progressBar = $('.stage__progress-bar');
    if(progressBar) {
      const percent = ((current + 1) / steps.length) * 100;
      progressBar.style.width = `${percent}%`;
    }
  }

  const stepConfig = {
    title: {
      title: "Let's name this opportunity",
      hint: "Examples: Software Engineering Intern, Marketing Fellowship. Keep it short and clear."
    },
    description: {
      title: "Tell us more about this role",
      hint: "Describe responsibilities, requirements and benefits. Use bullets and short paragraphs."
    },
    type: {
      title: "What type of opportunity is this?",
      hint: "This helps students find relevant opportunities when they search."
    },
    location: {
      title: "Where will this take place?",
      hint: "Students often filter by location and remote options."
    },
    dates: {
      title: "When does this happen?",
      hint: "Set realistic deadlines to give students time to prepare quality applications."
    },
    eligibility: {
      title: "Who can apply?",
      hint: "Optional criteria to help the right candidates find you. Leave blank if open to all."
    },
    benefits: {
      title: "What's in it for them?",
      hint: "Compensation, learning opportunities, perks, career benefits."
    },
    requirements: {
      title: "What do you need from applicants?",
      hint: "Add specific requirements. Mark non-critical items as optional."
    },
    questions: {
      title: "Any additional questions?",
      hint: "Custom questions beyond the standard application form."
    },
    review: {
      title: "Ready to publish?",
      hint: "Review your opportunity details before making it live."
    }
  };

  function showStep(index){
    current = Math.max(0, Math.min(steps.length-1, index));
    updateProgress();
    
    const stepKey = steps[current];
    const config = stepConfig[stepKey];
    
    // Update title and hint
    $('#title').textContent = config.title;
    $('.stage__hint').textContent = config.hint;
    
    // Show only current step - force hide all first, then show current
    steps.forEach((k, i)=>{
      const el = $(`[data-step="${k}"]`);
      if(!el) return;
      
      if(i === current) {
        el.classList.remove('hidden');
        // Focus after a short delay to ensure visibility
        setTimeout(() => {
          const focusEl = el.querySelector('.input, .input--xl, [contenteditable="true"], button, input, textarea, select');
          if(focusEl) focusEl.focus();
        }, 100);
      } else {
        el.classList.add('hidden');
      }
    });

    // Special handling for review step
    if(stepKey === 'review') {
      renderReview();
    }

    // Toggle CTA visibility
    $('#prev').disabled = current === 0;
    $('#next').classList.toggle('hidden', current === steps.length-1);
    $('#publish').classList.toggle('hidden', current !== steps.length-1);
  }

  function next(){ 
    // Basic validation before advancing
    const stepKey = steps[current];
    if(stepKey === 'title') {
      const title = $('input[name="title"]').value.trim();
      if(!title) {
        Components?.showToast?.('Please enter a title', 'error');
        return;
      }
    }
    if(stepKey === 'description') {
      const desc = $('#desc')?.innerHTML?.trim();
      if(!desc || desc === '<br>') {
        Components?.showToast?.('Please add a description', 'error');
        return;
      }
    }
    if(stepKey === 'location') {
      const location = $('input[name="location"]').value.trim();
      if(!location) {
        Components?.showToast?.('Please enter a location', 'error');
        return;
      }
    }
    if(stepKey === 'dates') {
      const startDate = $('input[name="start_date"]').value;
      const deadline = $('input[name="application_deadline"]').value;
      if(!startDate || !deadline) {
        Components?.showToast?.('Please set both dates', 'error');
        return;
      }
    }
    
    showStep(current+1); 
  }
  function prev(){ showStep(current-1); }

  function collectData(){
    const form = $('#wizardForm');
    const data = Utils.getFormData(form);
    // Contenteditable description
    data.description = $('#desc')?.innerHTML?.trim() || '';
    data.opportunity_type = typeValue;
    // Builder collections
    const reqs = $$('#requirementsList .builder__item').map((li, idx)=>({
      requirement: li.querySelector('input[name="requirement"]').value.trim(),
      is_mandatory: li.querySelector('input[name="mandatory"]').checked,
      order: idx
    })).filter(r=> r.requirement.length);
    const qs = $$('#questionsList .builder__item').map((li, idx)=>{
      const t = li.querySelector('select[name="question_type"]').value;
      const optionsRaw = li.querySelector('input[name="options"]').value.trim();
      let options = null;
      if(optionsRaw) options = optionsRaw.split(',').map(s=> s.trim()).filter(Boolean);
      return {
        question: li.querySelector('input[name="question"]').value.trim(),
        question_type: t,
        is_required: li.querySelector('input[name="is_required"]').checked,
        placeholder: li.querySelector('input[name="placeholder"]').value.trim(),
        help_text: li.querySelector('input[name="help_text"]').value.trim(),
        max_length: li.querySelector('input[name="max_length"]').value ? Number(li.querySelector('input[name="max_length"]').value) : null,
        min_length: li.querySelector('input[name="min_length"]').value ? Number(li.querySelector('input[name="min_length"]').value) : null,
        options,
        order: idx
      };
    }).filter(q=> q.question.length);
    data.requirements = reqs;
    data.additional_questions = qs;
    // datetime-local -> ISO
    if(data.application_deadline){
      const dt = new Date(data.application_deadline);
      data.application_deadline = dt.toISOString();
    }
    return data;
  }

  async function publish(){
    const payload = collectData();
    // basic validation steps
    if(!payload.title) { showStep(0); return; }
    if(!payload.description) { showStep(1); return; }
    try {
      Components?.showLoading?.(true);
      await window.api.opportunities.create(payload);
      Components?.showToast?.('Opportunity published', 'success');
      window.location.href = '/organization/dashboard.html';
    } catch(err){
      Components?.showToast?.(err.message || 'Failed to publish', 'error');
    } finally { Components?.showLoading?.(false); }
  }

  function bindKeyboard(){
    // Enter confirms step; Shift+Enter inserts newline in editor
    document.addEventListener('keydown', (e)=>{
      const inEditor = document.activeElement === $('#desc');
      if(inEditor){
        if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); next(); }
        return;
      }
      if(e.key === 'Enter'){
        e.preventDefault();
        next();
      }
    });
  }

  function addRequirementRow(value='', mandatory=true){
    const li = document.createElement('li');
    li.className = 'builder__item';
    li.innerHTML = `
      <input class="input" name="requirement" placeholder="Requirement" value="${Utils.escapeHTML(value)}">
      <label class="check"><input type="checkbox" name="mandatory" ${mandatory?'checked':''}> Mandatory</label>
      <button type="button" class="btn btn-sm" aria-label="Remove">Remove</button>
    `;
    li.querySelector('button').addEventListener('click', ()=> li.remove());
    $('#requirementsList').appendChild(li);
  }

  function addQuestionRow(){
    const li = document.createElement('li');
    li.className = 'builder__item';
    li.innerHTML = `
      <input class="input" name="question" placeholder="Ask a question (e.g., Why are you a good fit?)">
      <select class="input" name="question_type">
        <option value="text">Short Text</option>
        <option value="textarea">Long Text</option>
        <option value="number">Number</option>
        <option value="email">Email</option>
        <option value="url">URL</option>
        <option value="date">Date</option>
        <option value="file">File Upload</option>
        <option value="select">Multiple Choice</option>
        <option value="checkbox">Checkbox</option>
      </select>
      <button type="button" class="btn btn-sm" aria-label="Remove">Remove</button>
      <input class="input" name="placeholder" placeholder="Placeholder (optional)">
      <input class="input" name="help_text" placeholder="Help text (optional)">
      <div class="row">
        <input class="input" name="min_length" placeholder="Min length (optional)" type="number">
        <input class="input" name="max_length" placeholder="Max length (optional)" type="number">
      </div>
      <input class="input" name="options" placeholder="Options (comma-separated) for select/checkbox">
      <label class="check"><input type="checkbox" name="is_required"> Required</label>
    `;
    li.querySelector('button').addEventListener('click', ()=> li.remove());
    $('#questionsList').appendChild(li);
  }

  function renderReview(){
    const d = collectData();
    const el = $('#review');
    el.innerHTML = `
      <div><span class="chip">Title</span> ${Utils.escapeHTML(d.title||'')}</div>
      <div><span class="chip">Type</span> ${Utils.escapeHTML(d.opportunity_type||'')}</div>
      <div><span class="chip">Location</span> ${Utils.escapeHTML(d.location||'')}${d.is_remote?' (Remote)':''}</div>
      <div><span class="chip">Start</span> ${Utils.escapeHTML(d.start_date||'')} · <span class="chip">Deadline</span> ${Utils.escapeHTML(new Date(d.application_deadline||'').toLocaleString()||'')}</div>
      <div><span class="chip">Compensation</span> ${Utils.escapeHTML(d.compensation||'—')}</div>
      <div><span class="chip">Requirements</span> ${d.requirements.map(r=> r.requirement).join('; ') || '—'}</div>
      <div><span class="chip">Questions</span> ${d.additional_questions.length}</div>
    `;
  }

  function bindSegmented(){
    const group = $('.segmented'); if(!group) return;
    group.addEventListener('click', (e)=>{
      const btn = e.target.closest('.seg'); if(!btn) return;
      $$('.seg', group).forEach(b=> b.classList.remove('is-active'));
      btn.classList.add('is-active');
      typeValue = btn.getAttribute('data-value');
    });
  }

  function bindNav(){
    $('#next').addEventListener('click', next);
    $('#prev').addEventListener('click', prev);
    $('#publish').addEventListener('click', publish);
    $('#saveExit').addEventListener('click', async ()=>{
      try{
        Components?.showLoading?.(true);
        // Save draft (same endpoint for now; backend may accept "is_draft")
        const payload = { ...collectData(), is_draft: true };
        await window.api.opportunities.create(payload);
        Components?.showToast?.('Draft saved', 'success');
        window.location.href = '/organization/dashboard.html';
      }catch(err){
        Components?.showToast?.(err.message || 'Failed to save draft', 'error');
      } finally { Components?.showLoading?.(false); }
    });
  }

  function init(){
    mountNavbar();
    bindNav();
    bindKeyboard();
    bindSegmented();
    $('#addRequirement')?.addEventListener('click', ()=> addRequirementRow());
    $('#addQuestion')?.addEventListener('click', addQuestionRow);
    // Initial rows for guidance
    addRequirementRow('Motivated to learn', true);
    addRequirementRow('Time commitment 20h/week', false);
    showStep(0);
    
    // Remove the observer since we're handling review in showStep
  }

  document.addEventListener('DOMContentLoaded', init);
})();
