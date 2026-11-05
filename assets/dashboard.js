const $ = (id) => document.getElementById(id);
const fmt = (v) => Number(v || 0).toLocaleString(undefined, { maximumFractionDigits: 2 });
let currentData = null;

function drawLineChart(canvas, rows) {
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 600;
  const height = canvas.clientHeight || 190;
  canvas.width = width * dpr; canvas.height = height * dpr;
  ctx.scale(dpr, dpr); ctx.clearRect(0, 0, width, height);
  const values = rows.slice(-30).map(r => Number(r.response_time_ms || 0));
  if (!values.length) return;
  const pad = {l: 38, r: 12, t: 14, b: 25};
  const plotW = width - pad.l - pad.r, plotH = height - pad.t - pad.b;
  const max = Math.max(100, ...values) * 1.18;
  ctx.font = '9px DM Sans'; ctx.textAlign = 'right'; ctx.fillStyle = '#7187a1'; ctx.strokeStyle = 'rgba(133,157,184,.13)'; ctx.lineWidth = 1;
  for (let i=0;i<4;i++) { const y=pad.t+plotH*i/3; ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(width-pad.r,y);ctx.stroke();ctx.fillText(Math.round(max*(1-i/3)),pad.l-8,y+3); }
  const points = values.map((v,i)=>({x:pad.l+(values.length===1?plotW/2:i*plotW/(values.length-1)),y:pad.t+plotH-(v/max)*plotH}));
  const gradient = ctx.createLinearGradient(0,pad.t,0,height-pad.b); gradient.addColorStop(0,'rgba(69,213,229,.23)');gradient.addColorStop(1,'rgba(69,213,229,0)');
  ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.lineTo(points[points.length-1].x,height-pad.b);ctx.lineTo(points[0].x,height-pad.b);ctx.closePath();ctx.fillStyle=gradient;ctx.fill();
  ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle='#45d5e5';ctx.lineWidth=2;ctx.stroke();
  points.forEach(p=>{ctx.beginPath();ctx.arc(p.x,p.y,2.4,0,Math.PI*2);ctx.fillStyle='#45d5e5';ctx.fill();});
  ctx.textAlign='center';ctx.fillStyle='#7187a1';ctx.fillText('Older checks',pad.l+36,height-6);ctx.fillText('Latest',width-pad.r-18,height-6);
}
function drawDonut(canvas, counts) {
  const ctx=canvas.getContext('2d'), dpr=window.devicePixelRatio||1, w=canvas.clientWidth||200,h=canvas.clientHeight||150;
  canvas.width=w*dpr;canvas.height=h*dpr;ctx.scale(dpr,dpr);ctx.clearRect(0,0,w,h);
  const vals=[counts.up,counts.down,counts.slow], colors=['#43d6a0','#ff6b81','#ffbd70'];
  const total=vals.reduce((a,b)=>a+b,0); const cx=w/2,cy=h/2,r=Math.min(w,h)*.39,thickness=Math.max(11,r*.25);
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.strokeStyle='#26364b';ctx.lineWidth=thickness;ctx.stroke();
  if(total){let angle=-Math.PI/2;vals.forEach((v,i)=>{if(!v)return;const next=angle+(v/total)*Math.PI*2;ctx.beginPath();ctx.arc(cx,cy,r,angle,next);ctx.strokeStyle=colors[i];ctx.lineWidth=thickness;ctx.lineCap='round';ctx.stroke();angle=next;});}
}
function statePill(state){return `<span class="pill ${state}">${state}</span>`;}
function shortTime(value){if(!value)return 'Not checked';const date=new Date(value);return Number.isNaN(date.getTime())?'—':date.toLocaleString([], {month:'short',day:'2-digit',hour:'2-digit',minute:'2-digit',timeZone:'UTC'});}
function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function render(data){
  currentData=data;
  $('uptime').textContent=data.total_checks?fmt(data.overall_uptime_percent):'—';
  $('latency').textContent=fmt(data.average_response_time_ms);
  $('checks').textContent=fmt(data.total_checks);
  $('incidents').textContent=fmt(data.incident_checks);
  $('uptime-bar').style.width=`${Math.min(100,data.overall_uptime_percent||0)}%`;
  $('latency-bar').style.width=`${Math.min(100,(data.average_response_time_ms/(data.latency_threshold_ms||2000))*100)}%`;
  $('checks-bar').style.width=`${Math.min(100,data.total_checks*2)}%`;
  $('incident-bar').style.width=`${Math.min(100,data.incident_checks*10)}%`;
  $('threshold').textContent=`Alert threshold · ${fmt(data.latency_threshold_ms)} ms`;
  $('updated').textContent=`Report generated · ${shortTime(data.generated_at)} UTC`;
  $('endpoint-count').textContent=data.targets.length;
  $('table-summary').textContent=`${data.targets.length} configured endpoint(s) · ${data.total_checks} historical checks`;
  const down=data.targets.some(t=>t.state==='DOWN'), slow=data.targets.some(t=>t.state==='SLOW');
  const banner=$('banner');banner.classList.toggle('down',down);banner.classList.toggle('warning',!down&&slow);
  $('banner-check').textContent=down?'!':slow?'↗':'✓';
  $('banner-title').textContent=down?'Service interruption detected':slow?'A monitored endpoint is responding slowly':data.total_checks?'All monitored endpoints operational':'Waiting for first health check';
  $('banner-subtitle').textContent=down?'One or more monitored endpoints returned an error or could not be reached. Review endpoint details below.':slow?'At least one endpoint exceeded the configured response-time threshold.':'Run the Python monitoring script to refresh endpoint health and historical metrics.';
  const counts=data.targets.reduce((a,t)=>{if(t.state==='UP')a.up++;else if(t.state==='DOWN')a.down++;else a.slow++;return a;},{up:0,down:0,slow:0});
  $('healthy-count').textContent=counts.up;$('up-count').textContent=counts.up;$('down-count').textContent=counts.down;$('slow-count').textContent=counts.slow;
  $('incident-caption').textContent=data.incident_checks?'⚠ Downtime checks recorded':'✓ No DOWN events';
  $('incident-caption').className=data.incident_checks?'':'positive';
  $('endpoint-rows').innerHTML=data.targets.length?data.targets.map(t=>`<tr><td><div class="site"><span class="site-icon">${escapeHtml(t.name.slice(0,1).toUpperCase())}</span><div><b>${escapeHtml(t.name)}</b><small>${escapeHtml(t.url)}</small></div></div></td><td>${statePill(t.state)}</td><td>${t.http_status||'—'}</td><td class="latency-cell">${t.total_checks?fmt(t.response_time_ms)+' ms':'—'}</td><td class="uptime-cell">${t.total_checks?fmt(t.uptime_percent)+'%':'—'}</td><td>${shortTime(t.last_checked)}</td></tr>`).join(''):'<tr><td colspan="6" class="empty">No endpoints are configured.</td></tr>';
  const rows=(data.history||[]).slice(-8).reverse();
  $('activity-list').innerHTML=rows.length?rows.map(r=>`<div class="activity-row"><span class="activity-icon ${r.state}">${r.state==='UP'?'✓':r.state==='DOWN'?'!':'↗'}</span><div class="activity-copy"><b>${escapeHtml(r.name)} is ${escapeHtml(r.state)}</b><small>${escapeHtml(r.error||`HTTP ${r.http_status||'N/A'} · ${fmt(r.response_time_ms)} ms response`)}</small></div><span class="activity-time">${shortTime(r.timestamp_utc)}</span></div>`).join(''):'<div class="empty">Activity appears after the first monitoring cycle.</div>';
  $('chart-empty').style.display=(data.history||[]).length?'none':'grid';
  drawLineChart($('latencyChart'),data.history||[]);drawDonut($('healthChart'),counts);
}
async function refresh(){
  try{const response=await fetch('reports/dashboard-data.json?t='+Date.now());if(!response.ok)throw new Error('Monitoring report not found');const data=await response.json();render(data);}
  catch(error){$('updated').textContent='No report data found yet';$('banner-title').textContent='Monitoring data is not available';$('banner-subtitle').textContent='Run python monitor.py from the project folder, then refresh this dashboard.';console.info(error.message);}
}
$('refresh').addEventListener('click',refresh);
window.addEventListener('resize',()=>{if(currentData){drawLineChart($('latencyChart'),currentData.history||[]);const c=currentData.targets.reduce((a,t)=>{if(t.state==='UP')a.up++;else if(t.state==='DOWN')a.down++;else a.slow++;return a;},{up:0,down:0,slow:0});drawDonut($('healthChart'),c);}});
refresh();
