/* ══ PIXEL BLACKJACK STAND — game.js ═══════════════════════════════════════ */

// Map rank → filename prefix
const RANK_NAME = { A:'ace', J:'jack', Q:'queen', K:'king' };
// Map suit code → suit name
const SUIT_NAME = { S:'spades', H:'hearts', D:'diamonds', C:'clubs' };

let soundEnabled = true;
let _streak = 0, _streakDir = null;

/* ── Web Audio SFX ──────────────────────────────────────────────────────────── */
let _ctx = null;
function audioCtx() {
  if (!_ctx) _ctx = new (window.AudioContext || window.webkitAudioContext)();
  return _ctx;
}
function tone(freq, type, dur, vol=0.16) {
  if (!soundEnabled) return;
  try {
    const ctx = audioCtx(), osc = ctx.createOscillator(), g = ctx.createGain();
    osc.connect(g); g.connect(ctx.destination);
    osc.type = type; osc.frequency.value = freq;
    g.gain.setValueAtTime(vol, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
    osc.start(); osc.stop(ctx.currentTime + dur);
  } catch(e) {}
}
const SFX = {
  deal:      () => { tone(480,'sine',.07); setTimeout(()=>tone(600,'sine',.07),85); },
  hit:       () => tone(520,'triangle',.09),
  win:       () => [523,659,784,1047].forEach((f,i)=>setTimeout(()=>tone(f,'sine',.17),i*75)),
  blackjack: () => [523,659,784,1047,1319].forEach((f,i)=>setTimeout(()=>tone(f,'sine',.2),i*65)),
  lose:      () => { tone(330,'sawtooth',.08); setTimeout(()=>tone(220,'sawtooth',.17),75); },
  bust:      () => { tone(250,'sawtooth',.09); setTimeout(()=>tone(180,'sawtooth',.2),95); },
  push:      () => tone(440,'sine',.14),
  chip:      () => tone(800,'sine',.05,.1),
  ach:       () => [880,1100,1320].forEach((f,i)=>setTimeout(()=>tone(f,'sine',.14),i*55)),
};

function toggleSound() {
  soundEnabled = !soundEnabled;
  const b = document.getElementById('soundBtn');
  if (b) b.textContent = soundEnabled ? '🔊' : '🔇';
}

/* ── Card renderer using pixel PNG images ───────────────────────────────────── */
function cardFilename(card) {
  if (card.rank === '?') return null; // face-down
  const r = RANK_NAME[card.rank] || card.rank;
  const s = SUIT_NAME[card.suit]  || card.suit;
  return `${r}_of_${s}.png`;
}

function makeCardEl(card, delay=0) {
  const img = document.createElement('img');
  img.className = 'card-img';
  img.style.animationDelay = `${delay}s`;

  // base must be outside if/else — bug fix
  const base = (typeof CARDS_URL !== 'undefined') ? CARDS_URL : '/static/img/cards/';

  if (!card || card.rank === '?') {
    img.src = base + 'back.png';
    img.alt = 'Card back';
  } else {
    const fn = cardFilename(card);
    img.src = base + fn;
    img.alt = `${card.rank} of ${SUIT_NAME[card.suit]}`;
  }

  img.onerror = () => console.warn('Karta nenalezena:', img.src);
  return img;
}

function renderHand(id, cards, bjGlow=false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = '';
  (cards||[]).forEach((c,i) => {
    const img = makeCardEl(c, i * 0.07);
    if (bjGlow && cards.length===2) img.classList.add('bj-glow');
    el.appendChild(img);
  });
}

/* ── Bet controls ───────────────────────────────────────────────────────────── */
function addBet(v) {
  const inp = document.getElementById('betInput');
  if (!inp) return;
  inp.value = Math.min((parseInt(inp.value)||0) + v, currentChips);
  SFX.chip();
}
function clearBet() { const i = document.getElementById('betInput'); if(i) i.value=''; }
function betMax()   { const i = document.getElementById('betInput'); if(i){ i.value=currentChips; SFX.chip(); } }

/* ── Game API ───────────────────────────────────────────────────────────────── */
async function startGame() {
  const bet = Math.max(1, parseInt(document.getElementById('betInput')?.value || 50) || 50);
  show('ctrlBet', false);
  SFX.deal();
  const data = await call('/api/deal', { bet });
  if (!data) { show('ctrlBet', true); return; }
  applyState(data);
}

async function doHit()    { setActions(false); SFX.hit();  const d = await call('/api/hit');    if(d) applyState(d); }
async function doStand()  { setActions(false);             const d = await call('/api/stand');  if(d) applyState(d); }
async function doDouble() { setActions(false); SFX.chip(); const d = await call('/api/double'); if(d) applyState(d); }

async function call(url, body={}) {
  try {
    const r = await fetch(url, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    const d = await r.json();
    if (d.error) { showMsg('⚠ '+d.error, 'lose'); setActions(true); return null; }
    return d;
  } catch(e) { showMsg('⚠ Chyba připojení', 'lose'); setActions(true); return null; }
}

/* ── State handler ──────────────────────────────────────────────────────────── */
function applyState(data) {
  const bj = !data.hidden && data.pv===21 && data.player?.length===2;
  renderHand('playerHand', data.player, bj);
  renderHand('dealerHand', data.dealer);

  setTxt('pv', data.pv ?? '?');
  setTxt('dv', data.dv ?? '?');
  setTxt('betCount', data.bet ?? '—');

  const msg = document.getElementById('resultMsg');

  if (data.status === 'playing') {
    if (msg) { msg.textContent=''; msg.className='result-msg pixel'; }
    show('ctrlBet', false); show('ctrlPlay', true); show('ctrlNext', false);
    setActions(true);
    const dbl = document.getElementById('btnDouble');
    if (dbl) dbl.disabled = (data.player?.length>2) || data.doubled;
    return;
  }

  // Round over
  show('ctrlPlay', false); show('ctrlNext', true); show('ctrlBet', false);
  if (msg) { msg.textContent = data.message||''; msg.className = `result-msg pixel ${data.result||''}`; }

  // Sound
  const isNatBJ = data.player?.length===2 && data.pv===21;
  if (data.result==='win') { isNatBJ ? SFX.blackjack() : SFX.win(); }
  else if (data.result==='lose') { data.message?.includes('BUST') ? SFX.bust() : SFX.lose(); }
  else SFX.push();

  if (data.chips !== undefined) updateChips(data.chips);
  updateStreak(data.result);

  if (data.new_achievements?.length) { SFX.ach(); showAch(data.new_achievements); }
  if (data.chips !== undefined && data.chips <= 0) {
    setTimeout(() => show('brokeModal', true), 1100);
  }
}

/* ── Helpers ────────────────────────────────────────────────────────────────── */
function setTxt(id, v) { const e=document.getElementById(id); if(e) e.textContent=v; }

function show(id, vis) {
  const e = document.getElementById(id);
  if (!e) return;
  vis ? e.classList.remove('hidden') : e.classList.add('hidden');
}

function setActions(on) {
  ['btnHit','btnStand','btnDouble'].forEach(id => {
    const e = document.getElementById(id); if(e) e.disabled=!on;
  });
}

function resetRound() {
  ['playerHand','dealerHand'].forEach(id => {
    const e=document.getElementById(id);
    if(e) e.innerHTML='<div class="empty-hand pixel">'+( id==='playerHand' ? 'Vsaď a klikni DEAL!' : 'Čeká…')+'</div>';
  });
  const m=document.getElementById('resultMsg'); if(m){m.textContent='';m.className='result-msg pixel';}
  setTxt('pv','?'); setTxt('dv','?'); setTxt('betCount','—');
  show('ctrlBet',true); show('ctrlPlay',false); show('ctrlNext',false);
}

function updateChips(n) {
  currentChips = n;
  const e = document.getElementById('chipCount');
  if (!e) return;
  e.textContent = n.toLocaleString();
  e.classList.remove('chip-bump'); void e.offsetWidth; e.classList.add('chip-bump');
}

function showMsg(txt, cls='') {
  const e=document.getElementById('resultMsg');
  if(e) { e.textContent=txt; e.className=`result-msg pixel ${cls}`; }
}

function updateStreak(result) {
  if (result==='push') return;
  if (result===_streakDir) _streak++; else { _streak=1; _streakDir=result; }
  const e=document.getElementById('streakCount');
  if (!e) return;
  if (_streak>=2) {
    e.textContent = (_streakDir==='win'?'🔥':'❄️')+' '+_streak;
    e.style.color  = _streakDir==='win'?'#ff9f43':'#74b9ff';
  } else { e.textContent='—'; e.style.color=''; }
}

/* ── Refill ─────────────────────────────────────────────────────────────────── */
async function doRefill() {
  const d = await call('/api/refill');
  if (!d) return;
  updateChips(d.chips); show('brokeModal',false); showToast('💸 Dobito 500 žetonů!'); SFX.win();
}

/* ── Modals ─────────────────────────────────────────────────────────────────── */
function openRules()  { show('rulesModal',true); }
function closeRules() { show('rulesModal',false); }

/* ── Toast ──────────────────────────────────────────────────────────────────── */
function showToast(msg) {
  let t=document.getElementById('_toast');
  if(!t){ t=document.createElement('div'); t.id='_toast'; t.className='toast'; document.body.appendChild(t); }
  t.textContent=msg; t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3400);
}

/* ── Achievement popup ──────────────────────────────────────────────────────── */
let _achQ=[], _achBusy=false;
function showAch(list) { _achQ.push(...list); if(!_achBusy) _nextAch(); }
function _nextAch() {
  if (!_achQ.length) { _achBusy=false; return; }
  _achBusy=true;
  const a=_achQ.shift(), p=document.getElementById('achPopup');
  if (!p) { _nextAch(); return; }
  setTxt('apIcon', a.icon||'⭐');
  const n=document.getElementById('apName'); if(n){n.textContent=a.name||'';n.style.color=a.color||'#fff';}
  setTxt('apDesc', a.desc||''); setTxt('apRar', a.rarity||'');
  p.style.borderColor=a.color||'var(--gold)'; p.classList.add('show');
  setTimeout(()=>{ p.classList.remove('show'); setTimeout(_nextAch,350); },3600);
}

/* ── Init ───────────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('betInput')?.addEventListener('keydown', e => {
    if (e.key==='Enter') startGame();
  });

  document.addEventListener('keydown', e => {
    if (e.key==='Escape') { closeRules(); show('brokeModal',false); }
    const play=document.getElementById('ctrlPlay');
    if (!play || play.classList.contains('hidden')) {
      if (e.key==='Enter') {
        const bet=document.getElementById('ctrlBet');
        if (bet && !bet.classList.contains('hidden')) startGame();
        const next=document.getElementById('ctrlNext');
        if (next && !next.classList.contains('hidden')) resetRound();
      }
      return;
    }
    if (e.key==='h'||e.key==='H') doHit();
    if (e.key==='s'||e.key==='S') doStand();
    if (e.key==='d'||e.key==='D') doDouble();
  });

  document.getElementById('rulesModal')?.addEventListener('click', e => { if(e.target.id==='rulesModal') closeRules(); });
  document.getElementById('brokeModal')?.addEventListener('click', e => { if(e.target.id==='brokeModal') show('brokeModal',false); });
});
