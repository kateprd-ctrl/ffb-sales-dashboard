(function(){
  const RAW = window.__RAW || {};
  const loaders = {}, calcs = {}, cbs = [], cache = {}; let params = {}; let ready = false, pend = false;
  const colors = ['#d03040','#2f80d1','#e5a21b','#1f9d6b','#7b5cd6','#e0703a','#3aa7b5','#8a8f98'];
  function get(id){
    if (cache[id]) return cache[id];
    let r;
    try {
      if (calcs[id]) {
        const c = calcs[id];
        const ins = c.inputs.map(i => { const d = get(i); if (d.status !== 'ok') throw new Error('input ' + i + ': ' + d.message); return d.data; });
        const out = c.fn(...ins);
        r = { status: 'ok', data: out, columns: (out && out.columns) || (Array.isArray(out) && out[0] ? Object.keys(out[0]) : []), meta: [], refreshing: false, rows: out, value: out };
      } else if (loaders[id]) {
        const o = loaders[id].fn({ answer: RAW[id] });
        r = { status: 'ok', data: o.data, columns: o.columns || [], meta: o.meta || [], refreshing: false, rows: o.data, value: o.data };
      } else r = { status: 'missing', data: [], columns: [], message: 'нет данных ' + id };
    } catch (e) { console.error(id, e); r = { status: 'error', data: [], columns: [], message: String(e && e.message || e) }; }
    return (cache[id] = r);
  }
  function run(){ cbs.forEach(f => { try { f(); } catch (e) { console.error(e); } }); }
  function sched(){ if (!ready || pend) return; pend = true; setTimeout(() => { pend = false; run(); }, 0); }
  window.dash = {
    colors,
    data: get,
    onData(fn){ cbs.push(fn); },
    calc(id, o){ calcs[id] = o; },
    loader(id, o){ loaders[id] = o; },
    params(){ return Object.assign({}, params); },
    setParams(p){ Object.keys(p).forEach(k => { if (p[k] == null) delete params[k]; else params[k] = p[k]; }); Object.keys(calcs).forEach(k => delete cache[k]); sched(); },
    resetParams(){ params = {}; Object.keys(calcs).forEach(k => delete cache[k]); sched(); },
    refresh(){}, setLink(){}
  };
  window.addEventListener('load', () => { ready = true; run(); });
  let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(run, 120); });
})();
