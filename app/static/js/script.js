// app/static/js/script.js
(function(){
  const $ = (id)=>document.getElementById(id);

  function setOut(id, data){
    const box = $(id);
    if(!box) return;
    try{
      if(typeof data === "string") box.textContent = data;
      else box.textContent = JSON.stringify(data, null, 2);
    }catch(_){ box.textContent = String(data); }
  }

  function saveToken(tok){
    try{
      localStorage.setItem("mdc_token", tok || "");
      // سازگاری با کدهای قدیمی
      localStorage.setItem("token", tok || "");
      window.JWT = tok || "";
    }catch(_){}
  }
  function getToken(){
    try{ return (localStorage.getItem("mdc_token") || "").trim(); }
    catch(_){ return ""; }
  }

  async function api(url, opts={}){
    const headers = Object.assign({}, opts.headers||{});
    const token = getToken();
    if(token && !(opts.body instanceof FormData)){
      headers["Authorization"] = "Bearer " + token;
    }
    const r = await fetch(url, Object.assign({ method:"GET", headers }, opts));
    let data=null; try{ data = await r.json(); } catch(_){ data = null; }
    if(!r.ok) throw new Error((data && (data.detail||data.error)) || r.statusText);
    return data;
  }

  // Login
  $("btnLogin")?.addEventListener("click", async ()=>{
    try{
      const username = $("username")?.value || "admin";
      const password = $("password")?.value || "admin123";
      const form = new URLSearchParams(); form.set("username",username); form.set("password",password);
      const r = await fetch("/token", {
        method:"POST",
        headers:{ "Content-Type":"application/x-www-form-urlencoded" },
        body: form
      });
      const data = await r.json();
      if(!r.ok) throw new Error(data.detail || r.statusText);

      saveToken(data.access_token);
      setOut("outAuth", {ok:true, token:"*** stored ***"});

      try{ setOut("outMe", await api("/users/me")); }catch(err){ setOut("outMe", {error:String(err)}); }
      try{ setOut("outEtlNames", await api("/etl/names")); }catch(_){}
      try{ setOut("outConnections", await api("/db/connections")); }catch(_){}
    }catch(err){
      setOut("outAuth", {error:String(err)});
    }
  });

  // Preview CSV
  $("btnPreview")?.addEventListener("click", async ()=>{
    const f = $("csvFile")?.files?.[0];
    const max = $("maxRows")?.value || 5;
    if(!getToken()){ setOut("outPreview", {error:"Login first"}); return; }
    if(!f){ setOut("outPreview", {error:"No file selected"}); return; }
    const fd = new FormData(); fd.append("file", f, f.name);
    try{
      const r = await fetch(`/csv/preview?max_rows=${encodeURIComponent(max)}`, {
        method:"POST",
        headers: { "Authorization": "Bearer " + getToken() },
        body: fd
      });
      const data = await r.json();
      if(!r.ok) throw new Error(data.detail || r.statusText);
      setOut("outPreview", data);
    }catch(err){
      setOut("outPreview", {error:String(err)});
    }
  });

  // Load CSV
  $("btnLoad")?.addEventListener("click", async ()=>{
    const f = $("csvFile")?.files?.[0];
    const connId = $("connId")?.value || "1";
    const schema = $("schema")?.value || "sales";
    const table = $("tableName")?.value || "csv_import";
    const ifExists = $("ifExists")?.value || "append";
    if(!getToken()){ setOut("outLoad", {error:"Login first"}); return; }
    if(!f){ setOut("outLoad", {error:"No file selected"}); return; }

    const fd = new FormData();
    fd.append("conn_id", connId);
    fd.append("schema", schema);
    fd.append("table_name", table);
    fd.append("if_exists", ifExists);
    fd.append("file", f, f.name);

    try{
      const r = await fetch("/csv/load", {
        method:"POST",
        headers:{ "Authorization":"Bearer "+getToken() },
        body: fd
      });
      const data = await r.json();
      if(!r.ok) throw new Error(data.detail || r.statusText);
      setOut("outLoad", data);
    }catch(err){
      setOut("outLoad", {error:String(err)});
    }
  });

  // Upload dump
  $("btnUploadDump")?.addEventListener("click", async ()=>{
    const f = $("dumpFile")?.files?.[0];
    if(!getToken()){ setOut("outDump", {error:"Login first"}); return; }
    if(!f){ setOut("outDump", {error:"No file selected"}); return; }
    const fd = new FormData(); fd.append("file", f, f.name);
    try{
      const r = await fetch("/upload/dump", { method:"POST", headers:{ "Authorization":"Bearer "+getToken() }, body: fd });
      const data = await r.json();
      if(!r.ok) throw new Error(data.detail || r.statusText);
      setOut("outDump", data);
    }catch(err){
      setOut("outDump", {error:String(err)});
    }
  });

})();

// ====== Audit helpers ======
async function _callApi(path, opts = {}) {
  const token = (localStorage.getItem('mdc_token') || '').trim();
  const headers = new Headers(opts.headers || {});
  if (token) headers.set('Authorization', `Bearer ${token}`);
  return fetch(path, { ...opts, headers });
}
window.api = _callApi;

function _auditRenderTable(rows) {
  const el = document.getElementById('audit-table');
  if (!rows || rows.length === 0) {
    el.innerHTML = '<div style="padding: .75rem">رکوردی یافت نشد.</div>';
    return;
  }
  const body = rows.map(r => {
    const status = (r.status || '').toLowerCase();
    const badgeClass = status === 'success' ? 'ok' : (status === 'error' ? 'err' : 'warn');
    const meta = r.meta ? JSON.stringify(r.meta) : '';
    return `<tr>
      <td>${r.ts_utc ?? ''}</td>
      <td>${r.actor ?? ''}</td>
      <td>${r.ip ?? ''}</td>
      <td>${r.method ?? ''} <code>${r.path ?? ''}</code><br><small>req:${r.req_id ?? ''}</small></td>
      <td>${r.action ?? ''}</td>
      <td><span class="badge ${badgeClass}">${r.status ?? ''}</span></td>
      <td><code style="font-size:.8rem">${meta}</code></td>
    </tr>`;
  }).join('');
  document.getElementById('audit-table').innerHTML =
    `<div class="table-responsive"><table class="audit"><tbody>${body}</tbody></table></div>`;
}

async function auditFetchAndRender() {
  const token = (localStorage.getItem('mdc_token') || '').trim();
  const hint = document.getElementById('audit-hint');
  if (!token) { hint.textContent = ''; alert('ابتدا Login کنید.'); return; }

  const limit = Math.max(1, Math.min(500, parseInt(document.getElementById('audit-limit').value || '50', 10)));
  hint.textContent = 'در حال دریافت...';
  try {
    const res = await _callApi(`/audit/recent?limit=${limit}`, { method: 'GET' });

    const rlLimit = res.headers.get('x-ratelimit-limit');
    const rlRemain = res.headers.get('x-ratelimit-remaining');
    const reqId = res.headers.get('x-request-id');
    hint.textContent = `req:${reqId || '-'} | RL: ${rlRemain ?? '-'} / ${rlLimit ?? '-'}`;

    if (res.status === 429) {
      const retry = res.headers.get('retry-after') || '1';
      const j = await res.json().catch(() => ({}));
      alert(`درخواست زیاد بود (429). لطفاً ${retry}s دیگر تلاش کنید.\n${j.detail || ''}\nreq:${reqId || '-'}`);
      return;
    }
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      alert(`خطا در دریافت آدیت: ${res.status}\n${j.detail || ''}\nreq:${reqId || '-'}`);
      return;
    }
    const data = await res.json();
    _auditRenderTable(Array.isArray(data) ? data : []);
  } catch (e) {
    hint.textContent = '';
    alert('خطا در ارتباط با سرور: ' + e);
  }
}

async function auditExportCSV() {
  const token = (localStorage.getItem('mdc_token') || '').trim();
  if (!token) { alert('ابتدا Login کنید.'); return; }

  const limit = Math.max(1, Math.min(500, parseInt(document.getElementById('audit-limit').value || '50', 10)));
  const res = await _callApi(`/audit/recent?limit=${limit}`, { method: 'GET' });
  const rows = await res.json().catch(() => []);
  const csv = (function(rows){
    if (!rows || !rows.length) return '';
    const cols = ["id","ts_utc","actor","ip","method","path","action","status","req_id","user_agent","meta"];
    const esc = v => {
      if (v == null) return '';
      const s = typeof v === 'string' ? v : JSON.stringify(v);
      return `"${String(s).replaceAll(`"`,`""`)}"`;
    };
    const lines = [cols.join(',')].concat(rows.map(r => cols.map(c => esc(r[c])).join(',')));
    return lines.join('\r\n');
  })(rows);

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `audit_${new Date().toISOString().replace(/[:.]/g,'-')}.csv`;
  document.body.appendChild(a);
  a.click();
  URL.revokeObjectURL(url);
  a.remove();
}

document.addEventListener('DOMContentLoaded', () => {
  const btnRefresh = document.getElementById('btn-audit-refresh');
  const btnExport = document.getElementById('btn-audit-export');
  if (btnRefresh) btnRefresh.addEventListener('click', auditFetchAndRender);
  if (btnExport) btnExport.addEventListener('click', auditExportCSV);
  // دیگه در لود اولیه آدیت را خودکار نمی‌گیریم تا ۴۰۱ نبینیم
});
