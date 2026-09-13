(() => {
  'use strict';
  const process = JSON.parse(document.getElementById('case-data').textContent);
  const $ = id => document.getElementById(id);
  const money = value => new Intl.NumberFormat('pt-BR', {style:'currency',currency:'BRL'}).format(value);
  let currentDocument = null, page = 1, chatOpen = false, pending = false;
  const urls = new Map();
  const history = [];
  $('party').textContent = process.name;
  $('number').textContent = process.id;
  $('status').textContent = process.status;
  $('chat-number').textContent = process.id;
  $('doc-count').textContent = process.documents.length;
  const timeline = process.timeline || {events: []};
  const policy = process.policy || null;
  const timelineEvents = [...(timeline.events || [])].sort((left,right) => {
    const leftDate = typeof left.date === 'string' ? left.date : '';
    const rightDate = typeof right.date === 'string' ? right.date : '';
    return rightDate.localeCompare(leftDate);
  });
  $('timeline-count').textContent = timelineEvents.length;
  const processStartDate = process.start_date ? formatTimelineDate(process.start_date) : 'Não informada';
  for (const [label, value] of [['Instituição',process.bank],['Vara / tribunal',process.court],['Valor da causa',money(process.amount)],['Data de início do processo',processStartDate],['Ação pendente',process.pending_action || 'Nenhuma ação pendente']]) {
    const group = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd');
    dt.textContent = label; dd.textContent = value; group.append(dt,dd); $('metadata').append(group);
  }
  function renderAnalysis() {
    const profile = process.author_profile || [];
    for (const item of profile) {
      const group=document.createElement('div'), dt=document.createElement('dt'), dd=document.createElement('dd');
      dt.textContent=item.label;dd.textContent=item.value;group.append(dt,dd);$('author-profile').append(group);
    }
    if (!policy) {
      $('strategy-card').className='analysis-empty';
      $('strategy-card').replaceChildren(document.createTextNode('A análise estratégica ainda não está disponível para este processo.'));
      $('strategy-metrics').hidden=true;
      $('strategy-explanation').textContent='O JSON do processo não contém o bloco de política de acordos.';
      return;
    }
    const recommendation=String(policy.next_recommended_action || 'Análise pendente');
    const agreement=/acordo/i.test(recommendation);
    $('strategy-action').textContent=agreement?'Buscar um acordo':'Defender a tese';
    $('strategy-kind').textContent=recommendation;
    const risk=String(policy.risk_level || 'não informado');
    $('strategy-risk').textContent=`Risco ${risk}`;
    $('strategy-risk').classList.add(risk.toLocaleLowerCase('pt-BR')==='alto'?'high':risk.toLocaleLowerCase('pt-BR')==='baixo'?'low':'medium');
    const values=[
      ['Proposta inicial',agreement?money(policy.proposed_value_initial || 0):'Não aplicável'],
      ['Teto para acordo',agreement?money(policy.proposed_value_maximum || 0):'Não aplicável'],
      ['Custo estimado da defesa',money(policy.estimated_operacional_cost || 0)],
    ];
    for(const [label,value] of values){
      const group=document.createElement('dl');group.className='strategy-metric';
      const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;group.append(dt,dd);$('strategy-metrics').append(group);
    }
    $('strategy-explanation').textContent=policy.decision_explanation || 'O JSON não contém uma justificativa textual para esta recomendação.';
  }
  renderAnalysis();
  function setTab(tab, focus=false) {
    document.querySelectorAll('[role=tab]').forEach(button => {
      const selected = button.dataset.tab === tab;
      button.setAttribute('aria-selected', String(selected)); button.tabIndex = selected ? 0 : -1;
      $('panel-'+button.dataset.tab).hidden = !selected;
      if (selected && focus) button.focus();
    });
  }
  const tabs = [...document.querySelectorAll('[role=tab]')];
  tabs.forEach((button,index) => {
    button.addEventListener('click',() => setTab(button.dataset.tab));
    button.addEventListener('keydown',event => {
      let next;
      if(event.key==='ArrowRight') next=(index+1)%tabs.length;
      if(event.key==='ArrowLeft') next=(index+tabs.length-1)%tabs.length;
      if(event.key==='Home') next=0;
      if(event.key==='End') next=tabs.length-1;
      if(next!==undefined){event.preventDefault();setTab(tabs[next].dataset.tab,true);}
    });
  });
  function documentUrl(doc) {
    if(!urls.has(doc.id)) {
      const bytes = Uint8Array.from(atob(doc.base64), c => c.charCodeAt(0));
      urls.set(doc.id, URL.createObjectURL(new Blob([bytes],{type:'application/pdf'})));
    }
    return urls.get(doc.id);
  }
  function renderPage() {
    if(!currentDocument) return;
    $('page-label').textContent=`Página ${page} de ${currentDocument.pages}`;
    $('previous').disabled=page<=1; $('next').disabled=page>=currentDocument.pages;
    const preview=currentDocument.previews[page-1];
    const node=document.createElement(preview.image?'img':'pre');
    if(preview.image){node.src='data:image/png;base64,'+preview.image;node.alt=`${currentDocument.name} — página ${page}`;node.className='pdf-page';}
    else{node.textContent='Prévia textual · Imagem não gerada\n\n'+preview.text;node.className='pdf-text';}
    $('pdf-container').replaceChildren(node);$('pdf-container').scrollTop=0;
  }
  function selectDocument(doc) {
    currentDocument=doc;page=1;
    document.querySelectorAll('.document-item').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.id===doc.id)));
    $('document-name').textContent=doc.name;
    $('document-size').textContent=`PDF · ${Math.ceil(doc.bytes/1024)} KB · ${doc.pages} página(s)`;
    $('download').hidden=false; $('download').href=documentUrl(doc);$('download').download=doc.filename;
    renderPage();
  }
  for(const doc of process.documents){
    const button=document.createElement('button');button.className='document-item';button.dataset.id=doc.id;button.setAttribute('aria-pressed','false');
    const icon=document.createElement('span');icon.className='file-symbol';icon.textContent='PDF';icon.setAttribute('aria-hidden','true');
    const label=document.createElement('span');label.textContent=doc.name;
    const sub=document.createElement('small');sub.textContent=`${doc.pages} página(s)`;label.append(sub);button.append(icon,label);
    button.addEventListener('click',()=>selectDocument(doc));$('document-list').append(button);
  }
  $('previous').addEventListener('click',()=>{if(page>1){page--;renderPage();}});
  $('next').addEventListener('click',()=>{if(currentDocument&&page<currentDocument.pages){page++;renderPage();}});
  $('previous').disabled=true;$('next').disabled=true;
  if(process.documents.length)selectDocument(process.documents[0]);
  function formatTimelineDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return 'Data não informada';
    const [year, month, day] = value.split('-');
    return `${day}/${month}/${year}`;
  }
  function renderTimeline() {
    const list = $('timeline-list');
    if (timeline.current_stage) {
      $('timeline-stage').hidden = false;
      $('timeline-stage').textContent = timeline.current_stage;
    }
    if (timeline.next_recommended_action) {
      $('timeline-summary').hidden = false;
      $('timeline-summary').textContent = `Próxima ação recomendada: ${timeline.next_recommended_action}`;
    }
    if (!timelineEvents.length) {
      const empty = document.createElement('p');
      empty.className = 'timeline-empty';
      empty.textContent = 'Ainda não há eventos extraídos dos autos para este processo.';
      list.append(empty);
      return;
    }
    for (const event of timelineEvents) {
      const item = document.createElement('article');
      item.className = 'timeline-event';
      const date = document.createElement('time');
      date.className = 'timeline-date';
      date.dateTime = event.date || '';
      date.textContent = formatTimelineDate(event.date);
      const marker = document.createElement('span');
      marker.className = 'timeline-marker';
      marker.setAttribute('aria-hidden', 'true');
      const card = document.createElement('div');
      card.className = 'timeline-card';
      const heading = document.createElement('h3');
      heading.textContent = event.title || 'Movimentação processual';
      const tags = document.createElement('div');
      tags.className = 'timeline-tags';
      for (const label of [event.stage, event.action_required]) {
        if (!label) continue;
        const tag = document.createElement('span');
        tag.textContent = label;
        tags.append(tag);
      }
      const summary = document.createElement('p');
      summary.textContent = event.summary || 'Sem descrição disponível.';
      card.append(heading, tags, summary);
      item.append(date, marker, card);
      list.append(item);
    }
  }
  renderTimeline();
  function setChat(open){
    chatOpen=open;$('chat-panel').hidden=!open;$('workspace').classList.toggle('chat-open',open);
    $('chat-toggle').setAttribute('aria-expanded',String(open));$('chat-toggle').textContent=open?'✦ Recolher assistente':'✦ Abrir assistente';
    if(open)$('message-input').focus({preventScroll:true});else $('chat-toggle').focus({preventScroll:true});
  }
  $('chat-toggle').addEventListener('click',()=>setChat(!chatOpen));$('chat-close').addEventListener('click',()=>setChat(false));
  function appendMessage(role,text){
    const node=document.createElement('div');node.className='message '+role;
    const author=document.createElement('strong');author.textContent=role==='user'?'VOCÊ':'ASSISTENTE · DEMONSTRAÇÃO';
    const body=document.createElement('span');body.textContent=text;node.append(author,body);$('messages').append(node);
    $('messages').scrollTop=$('messages').scrollHeight;return node;
  }
  async function requestAssistant({message,context,messages}){
    // O detalhe é renderizado em um iframe `about:`, sem host próprio.
    const apiBase = 'http://127.0.0.1:8000';
    const response = await fetch(`${apiBase}/api/v1/monitoring/process/${encodeURIComponent(context.processId)}/assistant`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message, history: messages}),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.detail || 'Não foi possível consultar o assistente.');
    const sources = (payload.sources || []).length ? `\n\nFontes consultadas: ${payload.sources.join(' · ')}` : '';
    return {content: `${payload.answer}${sources}`};
  }
  appendMessage('assistant',`Olá! Posso responder perguntas sobre o processo de ${process.name} com base nos PDFs e no JSON de monitoramento deste caso.`);
  const input=$('message-input');
  input.addEventListener('input',()=>{$('send').disabled=pending||!input.value.trim();});
  input.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();sendMessage();}});
  $('chat-form').addEventListener('submit',event=>event.preventDefault());
  $('send').addEventListener('click',sendMessage);
  async function sendMessage(){
    const message=input.value.trim();if(!message||pending)return;
    history.push({role:'user',content:message});appendMessage('user',message);input.value='';pending=true;$('send').disabled=true;
    const waiting=appendMessage('assistant','Consultando os documentos e o histórico do processo…');
    try{
      const context={processId:process.id};
      const response=await requestAssistant({message,context,messages:history.slice(0,-1)});waiting.remove();history.push({role:'assistant',content:response.content});appendMessage('assistant',response.content);
    }catch(error){waiting.remove();appendMessage('assistant',error.message || 'Não foi possível responder. Tente enviar a mensagem novamente.');}
    finally{pending=false;$('send').disabled=!input.value.trim();}
  }
  window.addEventListener('pagehide',()=>urls.forEach(url=>URL.revokeObjectURL(url)));
})();
