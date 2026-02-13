#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/packages/protocol/src:$ROOT/packages/geo/src:$ROOT/apps/api/src:$ROOT/apps/simulator/src:${PYTHONPATH:-}"

cleanup(){
  kill ${SIM_PID:-} ${API_PID:-} ${WEB_PID:-} >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

python -m hyperdispatch_api.server &
API_PID=$!
python -m hyperdispatch_sim.runner --seed 1337 --drivers 20 --requests 30 --live &
SIM_PID=$!

build_web() {
  cd "$ROOT/apps/web"
  if [[ -d node_modules ]]; then
    npm run build && return 0
  fi
  return 1
}

fallback_web() {
  mkdir -p "$ROOT/apps/web/dist"
  cat > "$ROOT/apps/web/dist/index.html" <<'HTML'
<!doctype html><html><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/><title>HyperDispatch Demo</title>
<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>
<style>body{margin:0;background:#0b0f14;color:#e5eef9;font-family:Inter,system-ui}#app{display:grid;grid-template-columns:280px 1fr;height:100vh}.side{padding:16px;background:#111827;border-right:1px solid #263041}.panel{background:#111827;border:1px solid #2b3645;border-radius:10px;padding:12px}.main{padding:16px;display:grid;grid-template-rows:auto 1fr;gap:12px}#map{height:100%;border-radius:10px}.dot{width:10px;height:10px;border-radius:99px;background:#22c55e;border:2px solid #020617}.rider{background:#f97316}.ticker{max-height:280px;overflow:auto;font-size:12px}</style></head>
<body><div id='app'><div class='side'><h2>Uber HyperDispatch</h2><p>Control Tower</p><div class='panel'><div id='stats'>loading...</div></div><h3>Events</h3><div id='events' class='ticker'></div></div><div class='main'><div class='panel'>Live Fleet Map</div><div id='map'></div></div></div>
<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>
<script>
const map=L.map('map').setView([37.7749,-122.4194],12);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'OSM'}).addTo(map);
const markers={};const riders={};
async function tick(){
 try{const w=await (await fetch('/world')).json();
 document.getElementById('stats').textContent=`drivers: ${w.drivers.length} | riders: ${w.riders.length} | requests: ${w.requests.length}`;
 w.drivers.forEach(d=>{if(!markers[d.id]){markers[d.id]=L.circleMarker([d.lat,d.lon],{radius:6,color:'#22c55e'}).addTo(map);} markers[d.id].setLatLng([d.lat,d.lon]);});
 w.riders.forEach(r=>{if(!riders[r.id]){riders[r.id]=L.circleMarker([r.lat,r.lon],{radius:5,color:'#f97316'}).addTo(map);} riders[r.id].setLatLng([r.lat,r.lon]);});
 const ev=await (await fetch('/replay/events')).json();
 document.getElementById('events').innerHTML=(ev.events||[]).slice(-24).reverse().map(e=>`<div>${e.type} · ${new Date(e.ts).toLocaleTimeString()}</div>`).join('');
 }catch(e){}
}
setInterval(tick,1000);tick();
</script></body></html>
HTML
}

if ! build_web; then
  echo "[demo.sh] npm build unavailable; using offline static fallback"
  fallback_web
fi

python -m http.server 5173 --directory "$ROOT/apps/web/dist" >/dev/null 2>&1 &
WEB_PID=$!

echo "HyperDispatch demo up: api=http://127.0.0.1:8000 web=http://127.0.0.1:5173"
wait
