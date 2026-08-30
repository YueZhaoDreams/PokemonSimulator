const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];
let state = { decks: [], strategies: [], rulePresets: [], scanCards: [], scanCrops: [], chatId: null, history: [], chatMode: "list", chatLang: "zh", chatOpened: false, speakReplies: true, rules: null, user: null, users: [] };
const CHAT_STORE = "family-cup-chat-id";
const CHAT_LANG_STORE = "family-cup-chat-lang";
const CHAT_SPEAK_STORE = "family-cup-chat-speak";
const SFX_STORE = "family-cup-sfx";
const SHINY_STORE = "family-cup-shiny";
const RULE_STORE = "family-cup-rule";
const REDUCE = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const TYPE_TINT = {
  Grass: "#3dd68c",
  Fire: "#ff6b35",
  Water: "#4aa3ff",
  Lightning: "#ffcb05",
  Psychic: "#c77dff",
  Fighting: "#d97706",
  Darkness: "#7c5cff",
  Metal: "#9aa6b8",
  Fairy: "#ff8fab",
  Dragon: "#f59e0b",
  Colorless: "#d6d3d1",
  Trainer: "#60a5fa",
  Energy: "#fbbf24",
};

const CHIPS = [
  "你好！你会什么？",
  "Hi! What can you do?",
  "暴噬龟出现在起手 7 张的概率是多少？",
  "What is the probability Dondozo appears in the first 7 cards?",
  "帮两套牌对打，谁更强？",
  "Which cards should we trade so both sets get stronger?",
];

const CHAT_WELCOME = `你好！我是招式小熊 Combo Cub，可以直接跟我说话，也可以打字。
Hi! I’m Combo Cub — talk or type here and I’ll help with Family Cup.

中文和英文都可以。English or 中文 is fine.`;

const THEATER_BEATS = [
  "Shuffling both 30-card Family Cup decks…",
  "Setting 3 prize cards face-down…",
  "Mulligan until a Basic Pokémon…",
  "Attaching a Pokémon as matching energy…",
  "First player skips the draw and the attack…",
  "Checking paralysis, knockouts, and prize takes…",
];

async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  if (res.status === 401 && path !== "/api/auth/me" && path !== "/api/auth/login") {
    showAuthGate();
  }
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function showAuthGate() {
  document.body.classList.add("signed-out");
  closeCardSheet();
  $("#authGate")?.classList.remove("hidden");
  $("#accountBox")?.classList.add("hidden");
  shrinkAgent({ focusLauncher: false });
  $("#authEmail")?.focus();
}

function hideAuthGate() {
  document.body.classList.remove("signed-out");
  $("#authGate")?.classList.add("hidden");
}

function paintAccount() {
  const user = state.user;
  if (!user) {
    showAuthGate();
    return;
  }
  hideAuthGate();
  $("#accountBox")?.classList.remove("hidden");
  if ($("#accountEmail")) $("#accountEmail").textContent = user.email;
}

function clearClientSession() {
  state.user = null;
  state.decks = [];
  state.users = [];
  state.chatId = null;
  state.history = [];
  state.chatOpened = false;
  state.chatMode = "list";
  rememberChat(null);
}

async function submitAuth(register) {
  const email = $("#authEmail")?.value.trim();
  const password = $("#authPassword")?.value || "";
  $("#authError")?.classList.add("hidden");
  try {
    const user = await api(register ? "/api/auth/register" : "/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    state.chatId = null;
    state.history = [];
    state.chatOpened = false;
    state.chatMode = "list";
    rememberChat(null);
    state.user = user;
    shrinkAgent();
    await loadApp();
  } catch (err) {
    if ($("#authError")) {
      $("#authError").textContent = String(err.message || err).replace(/[{}"[\]]/g, " ").trim();
      $("#authError").classList.remove("hidden");
    }
  }
}

function show(view) {
  if (view === "chat") {
    openAgent();
    return;
  }
  if (!document.body.classList.contains("agent-open")) stopVoiceSession(false);

  if (view === "scan") view = "decks";
  closeCardSheet();
  $$("main > section").forEach((s) => s.classList.add("hidden"));
  $(`#view-${view}`).classList.remove("hidden");
  $$(".nav button").forEach((b) => {
    const on = b.dataset.view === view;
    b.classList.toggle("active", on);
    if (on) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
  if (view === "decks") {
    fillViewSet($("#viewSet")?.value);
    renderDecks();
    renderUsers();
  }
  if (view === "cards") {
    fillAddToSet($("#addToSet")?.value);
    paintCardPickerChrome();
  }
  if (view === "fight") fillFight();
  if (view === "lab") renderLab();
  ping("click");
}

function md(text) {
  return String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
    .replace(/\n/g, "<br>");
}

function esc(text) {
  return String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

function when(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

function aiLabel(ai) {
  if (ai?.chat?.configured) {
    const model = ai.chat.model || "cursor";
    if (ai.chat.ready === false) return `Cursor · ${model} (offline)`;
    return `Cursor · ${model}`;
  }
  if (ai?.vision?.configured) return `Vision · ${ai.vision.provider}`;
  if (ai?.configured) return `${ai.provider} · ${ai.model}`;
  return "Local coach";
}

function typeOf(card) {
  if (!card) return "Colorless";
  if (card.energy_type) return card.energy_type;
  if (Array.isArray(card.types) && card.types[0]) return card.types[0];
  const cat = String(card.category || "").toLowerCase();
  if (cat === "trainer") return "Trainer";
  if (cat === "energy") return "Energy";
  return "Colorless";
}

function typeMix(cards) {
  const counts = {};
  for (const card of cards || []) {
    const t = typeOf(card);
    counts[t] = (counts[t] || 0) + 1;
  }
  return Object.entries(counts).sort((a, b) => b[1] - a[1]);
}

function mixHtml(cards) {
  return typeMix(cards).slice(0, 4).map(([t, n]) =>
    `<span class="type-badge" style="background:${TYPE_TINT[t] || "#2a3548"};color:#0b1220">${esc(t)} ${n}</span>`
  ).join("");
}

function aceOf(deck) {
  const cards = deck?.cards || [];
  return cards.find((c) => c.image && String(c.category || "").toLowerCase() === "pokemon")
    || cards.find((c) => c.image)
    || cards[0]
    || null;
}

function classifyLog(line) {
  const text = String(line || "");
  if (/used .+ for \d+/i.test(text)) return "attack";
  if (/Knocked Out/i.test(text)) return "ko";
  if (/attaches|as .+ energy/i.test(text)) return "energy";
  if (/paralyz|asleep|burn|poison|confus/i.test(text)) return "status";
  if (/evolves/i.test(text)) return "evolve";
  if (/benches|plays |promotes|Switch|retreats/i.test(text)) return "play";
  if (/First player/i.test(text)) return "setup";
  return "note";
}

function cardTile(card, opts = {}) {
  const tint = TYPE_TINT[typeOf(card)] || TYPE_TINT.Colorless;
  const name = esc(card.name || "Unknown");
  const hp = card.hp ? `${card.hp} HP` : "";
  const img = card.image
    ? `<img src="${esc(card.image)}" alt="${name}" data-zoom="${esc(card.image)}" data-zoom-name="${name}">`
    : "";
  const replace = opts.deckId != null && opts.index != null
    ? `<button type="button" class="ghost quiet card-replace" data-replace-deck="${esc(opts.deckId)}" data-replace-idx="${opts.index}">Replace</button>`
    : "";
  return `<div class="card-tile holo" style="border-color:${tint}">
    ${hp ? `<span class="hp-pip">${esc(hp)}</span>` : ""}
    ${replace}
    ${img}
    <div class="meta"><b>${name}</b><span>${esc(card.category || "")} ${esc(card.stage || "")} ${hp}</span></div>
  </div>`;
}

function toast(msg, kind = "ok") {
  const el = $("#toast");
  if (!el) return;
  el.textContent = msg;
  el.className = `toast ${kind === "bad" ? "bad" : ""}`;
  el.classList.remove("hidden");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.add("hidden"), 2800);
}

const sfx = {
  on: false,
  ctx: null,
  ensure() {
    if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (this.ctx.state === "suspended") this.ctx.resume();
    return this.ctx;
  },
  beep(freq, dur, type = "square", gain = 0.04) {
    if (!this.on || REDUCE) return;
    try {
      const ctx = this.ensure();
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.type = type;
      osc.frequency.value = freq;
      g.gain.value = gain;
      osc.connect(g); g.connect(ctx.destination);
      osc.start();
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
      osc.stop(ctx.currentTime + dur);
    } catch {
      /* audio is optional stadium flavor */
    }
  },
};

function ping(kind) {
  if (kind === "click") sfx.beep(520, 0.05, "square", 0.03);
  if (kind === "win") { sfx.beep(523, 0.12, "triangle", 0.05); setTimeout(() => sfx.beep(784, 0.18, "triangle", 0.05), 90); }
  if (kind === "ko") sfx.beep(196, 0.16, "sawtooth", 0.04);
}

function paintSfx() {
  const btn = $("#sfxToggle");
  if (!btn) return;
  btn.textContent = sfx.on ? "SFX on" : "SFX off";
  btn.setAttribute("aria-pressed", sfx.on ? "true" : "false");
}

function loadChatLang() {
  try {
    const stored = localStorage.getItem(CHAT_LANG_STORE);
    if (stored === "zh" || stored === "en") {
      state.chatLang = stored;
      return;
    }
  } catch {
    /* private mode */
  }
  const nav = (navigator.language || "").toLowerCase();
  state.chatLang = nav.startsWith("zh") ? "zh" : "en";
}

function loadSpeakReplies() {
  try {
    const stored = localStorage.getItem(CHAT_SPEAK_STORE);
    if (stored === "0") state.speakReplies = false;
    if (stored === "1") state.speakReplies = true;
  } catch {
    /* private mode */
  }
}

function setChatLang(lang) {
  state.chatLang = lang === "en" ? "en" : "zh";
  try { localStorage.setItem(CHAT_LANG_STORE, state.chatLang); } catch { /* private mode */ }
  paintChatLang();
  if (voice.rec) voice.rec.lang = speechLang();
}

function toggleSpeakReplies() {
  state.speakReplies = !state.speakReplies;
  try { localStorage.setItem(CHAT_SPEAK_STORE, state.speakReplies ? "1" : "0"); } catch { /* private mode */ }
  if (!state.speakReplies) stopSpeech();
  paintChatLang();
}

function paintChatLang() {
  $("#chatLangZh")?.classList.toggle("active", state.chatLang === "zh");
  $("#chatLangEn")?.classList.toggle("active", state.chatLang === "en");
  const speak = $("#chatSpeak");
  if (speak) {
    speak.classList.toggle("active", state.speakReplies);
    speak.setAttribute("aria-pressed", state.speakReplies ? "true" : "false");
    speak.textContent = state.speakReplies ? "🔊 Speak replies · 朗读" : "🔇 Replies muted · 静音";
  }
  paintTalkButton();
}

function speechSupported() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

function ttsSupported() {
  return "speechSynthesis" in window;
}

function speechLang() {
  return state.chatLang === "zh" ? "zh-CN" : "en-US";
}

function speechLangFor(text) {
  if (/[\u3400-\u9fff]/.test(text || "")) return "zh-CN";
  if (/[A-Za-z]/.test(text || "")) return "en-US";
  return speechLang();
}

const voice = { rec: null, loop: false, speaking: false };

function paintTalkButton() {
  const mic = $("#chatMic");
  if (!mic) return;
  if (!speechSupported()) {
    mic.disabled = true;
    mic.textContent = "Mic unavailable · 无法语音";
    mic.setAttribute("aria-pressed", "false");
    return;
  }
  mic.disabled = false;
  if (voice.rec) {
    mic.classList.add("active");
    mic.setAttribute("aria-pressed", "true");
    mic.textContent = state.chatLang === "zh" ? "🎤 正在听… 点一下停止" : "🎤 Listening… tap to stop";
  } else if (voice.speaking) {
    mic.classList.add("active");
    mic.setAttribute("aria-pressed", "true");
    mic.textContent = state.chatLang === "zh" ? "🔊 正在说… 点一下打断" : "🔊 Speaking… tap to interrupt";
  } else {
    mic.classList.remove("active");
    mic.setAttribute("aria-pressed", "false");
    mic.textContent = state.chatLang === "zh" ? "🎤 说话" : "🎤 Talk";
  }
}

function speakableText(text) {
  const plain = String(text || "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/[_#>]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const bits = [];
  let buf = "";
  for (const ch of plain) {
    buf += ch;
    if ("。！？.!?".includes(ch)) {
      bits.push(buf.trim());
      buf = "";
    }
  }
  if (buf.trim()) bits.push(buf.trim());
  return (bits.slice(0, 4).join(" ") || plain).slice(0, 420);
}

function pickVoice(lang) {
  const voices = window.speechSynthesis.getVoices() || [];
  const want = (lang || "en-US").toLowerCase();
  return voices.find((v) => (v.lang || "").toLowerCase().startsWith(want.slice(0, 2))) || null;
}

function stopSpeech() {
  voice.speaking = false;
  if (ttsSupported()) window.speechSynthesis.cancel();
}

function stopVoiceListen() {
  const rec = voice.rec;
  voice.rec = null;
  if (rec) {
    try { rec.onend = null; rec.onerror = null; rec.stop(); } catch { /* already stopped */ }
  }
  paintTalkButton();
}

function chatViewOpen() {
  return document.body.classList.contains("agent-open");
}

function stopVoiceSession(keepLoop) {
  if (!keepLoop) voice.loop = false;
  sendChat.muteSpeak = true;
  sendChat.pending = null;
  stopVoiceListen();
  stopSpeech();
  paintTalkButton();
}

function paintAgentChrome() {
  const full = $("#agentFull");
  const on = document.body.classList.contains("agent-full");
  if (full) {
    full.setAttribute("aria-pressed", on ? "true" : "false");
    full.title = on ? "Split" : "Fullscreen";
    full.textContent = on ? "Split" : "Fullscreen";
  }
}

function openAgent() {
  document.body.classList.add("agent-open");
  const panel = $("#agentPanel");
  if (panel) panel.hidden = false;
  $("#cubLauncher")?.setAttribute("aria-expanded", "true");
  sendChat.muteSpeak = false;
  paintAgentChrome();
  renderChat();
  ping("click");
  $("#agentShrink")?.focus();
}

function shrinkAgent(opts = {}) {
  document.body.classList.remove("agent-open", "agent-full");
  const panel = $("#agentPanel");
  if (panel) panel.hidden = true;
  $("#cubLauncher")?.setAttribute("aria-expanded", "false");
  stopVoiceSession(false);
  paintAgentChrome();
  if (opts.focusLauncher !== false && !document.body.classList.contains("signed-out")) {
    $("#cubLauncher")?.focus();
  }
}

function toggleAgentFull() {
  if (!document.body.classList.contains("agent-open")) openAgent();
  document.body.classList.toggle("agent-full");
  paintAgentChrome();
}

function speakReply(text) {
  return new Promise((resolve) => {
    if (!state.speakReplies || !ttsSupported() || REDUCE) {
      resolve();
      return;
    }
    const spoken = speakableText(text);
    if (!spoken) {
      resolve();
      return;
    }
    stopSpeech();
    const utter = new SpeechSynthesisUtterance(spoken);
    utter.lang = speechLangFor(spoken);
    const chosen = pickVoice(utter.lang);
    if (chosen) utter.voice = chosen;
    utter.rate = utter.lang.startsWith("zh") ? 1 : 1.02;
    const done = () => {
      voice.speaking = false;
      paintTalkButton();
      resolve();
    };
    utter.onend = done;
    utter.onerror = done;
    voice.speaking = true;
    paintTalkButton();
    window.speechSynthesis.speak(utter);
  });
}

function startVoiceListen() {
  if (!speechSupported() || sendChat.streaming || voice.rec) return;
  stopSpeech();
  const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
  const rec = new Ctor();
  rec.lang = speechLang();
  rec.interimResults = true;
  rec.maxAlternatives = 1;
  rec.continuous = false;
  rec.onresult = (ev) => {
    let finalText = "";
    let live = "";
    for (let i = ev.resultIndex; i < ev.results.length; i += 1) {
      const chunk = ev.results[i][0]?.transcript || "";
      if (ev.results[i].isFinal) finalText += chunk;
      else live += chunk;
    }
    if ($("#chatInput")) $("#chatInput").value = (finalText || live).trim();
    if (finalText.trim()) {
      if (/[\u3400-\u9fff]/.test(finalText)) setChatLang("zh");
      else if (/[A-Za-z]/.test(finalText)) setChatLang("en");
      sendChat.fromVoice = true;
      rec.onend = () => {
        voice.rec = null;
        paintTalkButton();
      };
      try { rec.stop(); } catch { /* ignore */ }
      if (sendChat.busy || sendChat.streaming) {
        sendChat.pending = { message: finalText.trim(), fromVoice: true };
        stopSpeech();
      } else {
        sendChat();
      }
    }
  };
  rec.onend = () => {
    voice.rec = null;
    paintTalkButton();
  };
  rec.onerror = () => {
    voice.rec = null;
    paintTalkButton();
  };
  voice.rec = rec;
  paintTalkButton();
  try {
    rec.start();
  } catch {
    voice.rec = null;
    paintTalkButton();
  }
}

function toggleChatMic() {
  if (voice.speaking) {
    voice.loop = true;
    stopSpeech();
    startVoiceListen();
    return;
  }
  if (voice.rec) {
    voice.loop = false;
    stopVoiceListen();
    return;
  }
  if (!speechSupported() || sendChat.streaming) return;
  voice.loop = true;
  startVoiceListen();
}

function setBusy(on, line, withMask) {
  document.body.classList.toggle("busy", !!(on && withMask));
  const mask = $("#busyMask");
  if (mask) mask.classList.toggle("hidden", !(on && withMask));
  if (line && $("#busyLine")) $("#busyLine").textContent = line;
  if (!on) {
    stopTheater();
    if ($("#theaterLine")) $("#theaterLine").textContent = "";
  } else if (withMask) {
    startTheater();
  }
}

let theaterTimer = 0;
function startTheater() {
  stopTheater();
  if (REDUCE) return;
  const line = $("#theaterLine");
  if (!line) return;
  let i = 0;
  const tick = () => {
    const extra = theaterNames();
    const pool = THEATER_BEATS.concat(extra);
    line.textContent = pool[i % pool.length];
    i += 1;
  };
  tick();
  theaterTimer = setInterval(tick, 900);
}
function stopTheater() {
  if (theaterTimer) clearInterval(theaterTimer);
  theaterTimer = 0;
}
function theaterNames() {
  const a = state.decks.find((d) => d.id === $("#deckA")?.value);
  const b = state.decks.find((d) => d.id === $("#deckB")?.value);
  const names = [...(a?.cards || []), ...(b?.cards || [])].map((c) => c.name).filter(Boolean);
  const pick = names[Math.floor(Math.random() * Math.max(names.length, 1))] || "a Basic";
  return [
    `${pick} hits the bench…`,
    `Looking up ${pick} in the prize cards…`,
    `Wondering if ${pick} can close this game…`,
  ];
}

function paintRules(rules) {
  state.rules = rules;
  if (!rules) return;
  const energy = rules.pokemon_as_energy ? "Pokémon are energy" : "standard energy";
  const strip = $("#ruleStrip");
  if (strip) {
    const chips = [
      `${rules.deck_size} cards`,
      `${rules.prize_count} prizes`,
      `hand ${rules.opening_hand}`,
      rules.pokemon_as_energy ? "Pokémon = energy" : "No Pokémon energy",
    ];
    if (rules.extra_prize_for_ex) {
      chips.push("ex = 2 prizes · Mega ex = 3");
    }
    if (rules.max_copies_except_basic_energy) {
      chips.push(`max ${rules.max_copies_except_basic_energy} of a name`);
    }
    strip.innerHTML = chips.map((c) => `<span class="chip">${esc(c)}</span>`).join("");
  }
  const tag = $("#brandTag");
  if (tag) tag.textContent = `${rules.deck_size} cards · ${rules.prize_count} prizes · ${energy}`;
  ensurePrizePips();
  syncRulePreset(rules);
}

function syncRulePreset(rules) {
  const sel = $("#rulePreset");
  if (!sel || !sel.options.length) return;
  const want = rules?.pokemon_as_energy === false ? "c" : "b";
  if ([...sel.options].some((o) => o.value === want)) sel.value = want;
}

function prizeCount() {
  const n = Number(state.rules?.prize_count);
  return Number.isFinite(n) && n > 0 ? n : 3;
}

function ensurePrizePips() {
  const n = prizeCount();
  for (const id of ["prizesA", "prizesB"]) {
    const row = $(`#${id}`);
    if (!row) continue;
    if (row.children.length === n) continue;
    row.innerHTML = Array.from({ length: n }, () => "<i></i>").join("");
  }
}

function paintPrizes(winner) {
  ensurePrizePips();
  const n = prizeCount();
  const fill = (id, taken) => {
    $$(`#${id} i`).forEach((el, i) => el.classList.toggle("taken", i < taken));
  };
  if (winner === "a") { fill("prizesA", n); fill("prizesB", 0); }
  else if (winner === "b") { fill("prizesA", 0); fill("prizesB", n); }
  else if (winner === "tie") {
    const half = Math.floor(n / 2);
    fill("prizesA", half);
    fill("prizesB", half);
  } else {
    fill("prizesA", 0);
    fill("prizesB", 0);
  }
}

function resetArenaResult() {
  const stage = $("#arenaStage");
  if (!stage) return;
  stage.classList.remove("winner-a", "winner-b", "winner-tie");
  if ($("#vsBadge")) $("#vsBadge").textContent = "VS";
  paintPrizes(null);
}

function paintArena() {
  const stage = $("#arenaStage");
  if (!stage) return;
  const a = state.decks.find((d) => d.id === $("#deckA")?.value);
  const b = state.decks.find((d) => d.id === $("#deckB")?.value);
  const aceA = aceOf(a);
  const aceB = aceOf(b);
  const faceA = $("#faceA");
  const faceB = $("#faceB");
  if (faceA) {
    faceA.src = aceA?.image || "/static/icon.svg";
    faceA.alt = aceA?.name || "Deck A";
  }
  if (faceB) {
    faceB.src = aceB?.image || "/static/icon.svg";
    faceB.alt = aceB?.name || "Deck B";
  }
  if ($("#nameA")) $("#nameA").textContent = a?.name || "Deck A";
  if ($("#nameB")) $("#nameB").textContent = b?.name || "Deck B";
  if ($("#mixA")) $("#mixA").innerHTML = mixHtml(a?.cards);
  if ($("#mixB")) $("#mixB").innerHTML = mixHtml(b?.cards);
  const sa = state.strategies.find((s) => s.name === $("#stratA")?.value);
  const sb = state.strategies.find((s) => s.name === $("#stratB")?.value);
  if ($("#stratBlurb")) {
    $("#stratBlurb").textContent = [sa?.description, sb?.description].filter(Boolean).join("  ·  ");
  }
  if ($("#arenaHint") && a && b) {
    const winning = stage.classList.contains("winner-a") ? "a"
      : stage.classList.contains("winner-b") ? "b"
      : stage.classList.contains("winner-tie") ? "tie"
      : "";
    if (winning === "a") $("#arenaHint").textContent = `${a.name} takes it`;
    else if (winning === "b") $("#arenaHint").textContent = `${b.name} takes it`;
    else if (winning === "tie") $("#arenaHint").textContent = "Even match";
    else $("#arenaHint").textContent = `${a.name} vs ${b.name}`;
  }
}

async function loadApp() {
  paintAccount();
  const health = await api("/api/health");
  $("#aiPill").textContent = aiLabel(health.ai);
  if ($("#agentModel")) $("#agentModel").textContent = aiLabel(health.ai);
  state.decks = await api("/api/decks");
  state.strategies = await api("/api/strategies");
  try {
    state.rulePresets = await api("/api/rule-presets");
  } catch {
    state.rulePresets = [];
  }
  if (state.user?.role === "admin") {
    try {
      state.users = await api("/api/users");
    } catch {
      state.users = [];
    }
  } else {
    state.users = [];
  }
  fillFight();
  const remembered = rememberedRule();
  if (remembered && $("#rulePreset") && [...$("#rulePreset").options].some((o) => o.value === remembered)) {
    $("#rulePreset").value = remembered;
    const preset = state.rulePresets?.find((p) => p.preset === remembered);
    paintRules(preset || health.rules);
    fillFight();
  } else {
    paintRules(health.rules);
  }
  renderUsers();
  show("cards");
}

function renderUsers() {
  const panel = $("#userPanel");
  const list = $("#userList");
  if (!panel || !list) return;
  if (state.user?.role !== "admin") {
    panel.classList.add("hidden");
    return;
  }
  panel.classList.remove("hidden");
  list.innerHTML = (state.users || []).map((u) =>
    `<div class="tiny">${esc(u.email)} · ${esc(u.role)}</div>`
  ).join("") || `<p class="tiny">No other trainers yet.</p>`;
}

async function boot() {
  try {
    if (localStorage.getItem(SHINY_STORE) === "1") document.body.classList.add("shiny");
    sfx.on = localStorage.getItem(SFX_STORE) === "1";
  } catch {
    /* private mode */
  }
  paintSfx();
  loadChatLang();
  loadSpeakReplies();
  paintChatLang();
  CHIPS.forEach((q) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = q;
    b.onclick = () => {
      startNewChat();
      openAgent();
      $("#chatInput").value = q;
      sendChat();
    };
    $("#chips").appendChild(b);
  });
  $("#authForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    submitAuth(false);
  });
  $("#authRegister")?.addEventListener("click", () => submitAuth(true));
  $("#logoutBtn")?.addEventListener("click", async () => {
    try {
      await api("/api/auth/logout", { method: "POST" });
    } catch {
      /* already signed out */
    }
    clearClientSession();
    showAuthGate();
    shrinkAgent({ focusLauncher: false });
  });
  try {
    state.user = await api("/api/auth/me");
    await loadApp();
  } catch {
    showAuthGate();
  }
}

function rememberedRule() {
  try { return localStorage.getItem(RULE_STORE) || ""; } catch { return ""; }
}

function currentRule() {
  return $("#rulePreset")?.value || rememberedRule() || "b";
}

function rememberRule(key) {
  try { localStorage.setItem(RULE_STORE, key); } catch { /* private mode */ }
}

function ruleChoices() {
  const presets = state.rulePresets?.length
    ? state.rulePresets
    : [
        { preset: "b", label: "Pokémon = energy" },
        { preset: "c", label: "No Pokémon energy" },
      ];
  return presets.map((p) => ({
    preset: p.preset,
    label: p.preset === "c" ? "No Pokémon energy" : p.preset === "b" ? "Pokémon = energy" : (p.label || p.preset),
  }));
}

function deckRulePresets(d) {
  if (Array.isArray(d?.rule_presets) && d.rule_presets.length) {
    return d.rule_presets.filter((k) => k === "b" || k === "c");
  }
  const r = d?.rule_preset;
  if (r === "c") return ["c"];
  if (r === "b") return ["b"];
  return ["b", "c"];
}

function deckRulePreset(d) {
  const keys = deckRulePresets(d);
  if (keys.length === 1) return keys[0];
  if (d?.rule_preset) return d.rule_preset;
  return "any";
}

function decksMatchingRule(preset, { includeSpare = true } = {}) {
  const key = preset || currentRule();
  return (state.decks || []).filter((d) => {
    if (!includeSpare && d.kind === "spare") return false;
    return deckRulePresets(d).includes(key);
  });
}

function fillFight() {
  const keep = {
    a: $("#deckA")?.value,
    b: $("#deckB")?.value,
    sa: $("#stratA")?.value,
    sb: $("#stratB")?.value,
    rule: $("#rulePreset")?.value,
  };
  const pick = (sel, preferred, fallback) => {
    if (!sel) return;
    if (preferred && [...sel.options].some((o) => o.value === preferred)) sel.value = preferred;
    else if (fallback) sel.value = fallback;
  };
  const ruleSel = $("#rulePreset");
  if (ruleSel) {
    const presets = state.rulePresets?.length
      ? state.rulePresets
      : [
          { preset: "b", label: "Pokémon = energy" },
          { preset: "c", label: "No Pokémon energy" },
        ];
    ruleSel.innerHTML = presets
      .map((p) => {
        const label = p.preset === "c"
          ? "No Pokémon energy"
          : p.preset === "b"
            ? "Pokémon = energy"
            : (p.label || p.preset);
        return `<option value="${esc(p.preset)}">${esc(label)}</option>`;
      })
      .join("");
    const fallbackRule = state.rules?.pokemon_as_energy === false ? "c" : "b";
    pick(ruleSel, keep.rule, fallbackRule);
  }
  const rule = currentRule();
  const visible = decksMatchingRule(rule);
  for (const id of ["deckA", "deckB"]) {
    const sel = $(`#${id}`);
    if (!sel) continue;
    sel.innerHTML = visible.map((d) => `<option value="${esc(d.id)}">${esc(d.name)} (${d.count})</option>`).join("");
  }
  const lists = visible.filter((d) => d.kind !== "spare");
  const fallbackA = rule === "c"
    ? (lists.find((d) => d.id === "seed-e") || lists[0])
    : lists[0];
  const fallbackB = rule === "c"
    ? (lists.find((d) => d.id === "seed-f") || lists[1] || lists[0])
    : (lists[1] || lists[0]);
  pick($("#deckA"), keep.a, fallbackA?.id);
  pick($("#deckB"), keep.b, fallbackB?.id);
  for (const id of ["stratA", "stratB"]) {
    const sel = $(`#${id}`);
    if (!sel) continue;
    sel.innerHTML = state.strategies.map((s) => `<option value="${esc(s.name)}">${esc(s.name)}</option>`).join("");
  }
  const stratFallbackA = [...($("#stratA")?.options || [])].some((o) => o.value === "thrifty") ? "thrifty" : null;
  const stratFallbackB = [...($("#stratB")?.options || [])].some((o) => o.value === "shock") ? "shock" : null;
  pick($("#stratA"), keep.sa, stratFallbackA);
  pick($("#stratB"), keep.sb, stratFallbackB);
  const now = {
    a: $("#deckA")?.value,
    b: $("#deckB")?.value,
    sa: $("#stratA")?.value,
    sb: $("#stratB")?.value,
  };
  if (keep.a && (keep.a !== now.a || keep.b !== now.b || keep.sa !== now.sa || keep.sb !== now.sb)) {
    resetArenaResult();
  }
  paintArena();
}

function renderEditor() {
  const box = $("#editor");
  if (!box) return;
  const crops = (state.scanCrops || []).filter((c) => !c.removed);
  if (!crops.length && !state.scanCards.length) {
    box.innerHTML = `<p class="tiny">No cards yet. Scan a photo or load a sample.</p>`;
    return;
  }
  const cropHtml = state.scanCrops.length ? `<div class="crop-grid">${state.scanCrops.map((c, i) => {
    if (c.removed) return "";
    const review = c.needs_review || c.name === "Unknown" ? " review" : "";
    const shown = c.name === "Unknown" ? "" : c.name;
    return `<div class="crop-tile${review}">
      <img src="data:image/jpeg;base64,${c.jpeg_b64}" alt="">
      <input data-crop="${i}" value="${esc(shown)}" placeholder="Card name">
      <div class="tiny">${Math.round(c.confidence || 0)}%${c.needs_review ? " · check" : ""}</div>
      <button class="ghost" data-drop="${i}" type="button">✕</button>
    </div>`;
  }).join("")}</div>` : "";
  box.innerHTML = cropHtml + (cropHtml ? "" : state.scanCards.map((c, i) => `
    <div class="editor-row">
      <div class="grow"><b>${esc(c.name)}</b><div class="tiny">${esc(c.category)} ${esc(c.stage || "")} ${c.hp ? c.hp + " HP" : ""}</div></div>
      <button class="ghost" data-del="${i}">✕</button>
    </div>`).join("")) + `<p class="tiny">${state.scanCards.length} named cards</p>`;
  box.querySelectorAll("[data-del]").forEach((b) => {
    b.onclick = () => { state.scanCards.splice(+b.dataset.del, 1); renderEditor(); };
  });
  box.querySelectorAll("[data-drop]").forEach((b) => {
    b.onclick = () => { state.scanCrops[+b.dataset.drop].removed = true; syncCardsFromCrops(); renderEditor(); };
  });
  box.querySelectorAll("[data-crop]").forEach((input) => {
    input.onchange = () => renameCrop(+input.dataset.crop, input.value.trim());
  });
}

function syncCardsFromCrops() {
  if (!state.scanCrops.length) return;
  state.scanCards = state.scanCrops
    .filter((c) => !c.removed && c.name && c.name !== "Unknown")
    .map((c) => c.card || { name: c.name, category: "Pokemon" });
}

async function renameCrop(index, name) {
  const crop = state.scanCrops[index];
  if (!crop) return;
  if (!name) {
    crop.name = "Unknown";
    crop.card = null;
    crop.needs_review = true;
    syncCardsFromCrops();
    renderEditor();
    return;
  }
  try {
    const card = await api("/api/cards/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    crop.name = card.name;
    crop.card = card;
    crop.needs_review = false;
    crop.confidence = 100;
    syncCardsFromCrops();
    renderEditor();
    if (crop.jpeg_b64) {
      api("/api/recognize/learn", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: card.name, jpeg_b64: crop.jpeg_b64 }),
      }).catch(() => {});
    }
  } catch (err) {
    toast(err.message, "bad");
  }
}

function bindZoom(root) {
  root.querySelectorAll("[data-zoom]").forEach((img) => {
    img.onclick = () => openLightbox(img.dataset.zoom, img.dataset.zoomName || "");
  });
}

function bindReplace(root) {
  root.querySelectorAll("[data-replace-deck]").forEach((btn) => {
    btn.onclick = (e) => {
      e.stopPropagation();
      startReplace(btn.dataset.replaceDeck, +btn.dataset.replaceIdx);
    };
  });
}

let pickerTarget = null;
let pickerSeq = 0;
let cardSearchTimer = 0;
let searchSeq = 0;

function searchHitHtml(hits) {
  if (!hits.length) return `<p class="tiny">No matches yet. Keep typing, or Add to set with the name in the box.</p>`;
  const action = pickerTarget?.kind === "replace" ? "Replace" : "+";
  return hits.map((h) => `
    <button type="button" class="search-hit" data-card-id="${esc(h.id || "")}" data-card-name="${esc(h.name || "")}">
      ${h.image ? `<img src="${esc(h.image)}" alt="${esc(h.name || "")}">` : ""}
      <span>${esc(h.name || "")}</span>
      <span class="hit-add">${action}</span>
    </button>`).join("");
}

async function lookupCards(q, scope = "all") {
  const query = (q || "").trim();
  if (query.length < 2) return [];
  return api(`/api/cards/search?q=${encodeURIComponent(query)}&scope=${encodeURIComponent(scope)}`);
}

async function runCardSearch(q) {
  const box = $("#addHits");
  if (!box) return;
  const query = (q || "").trim();
  const seq = ++searchSeq;
  if (query.length < 2) {
    box.hidden = true;
    box.innerHTML = "";
    box.dataset.query = "";
    return;
  }
  box.hidden = false;
  box.innerHTML = `<p class="tiny">Looking up ${esc(query)}…</p>`;
  try {
    const local = await lookupCards(query, "local");
    if (seq !== searchSeq) return;
    paintHits(box, local);
    const all = await lookupCards(query, "all");
    if (seq !== searchSeq) return;
    paintHits(box, all);
  } catch (err) {
    if (seq !== searchSeq) return;
    toast(err.message, "bad");
  }
}

async function resolvePick(hit) {
  const payload = { name: hit.name };
  if (hit.id) payload.id = hit.id;
  return api("/api/cards/resolve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function paintHits(box, hits) {
  if (!box) return;
  box.hidden = false;
  box.dataset.query = ($("#addName")?.value || "").trim();
  box.innerHTML = searchHitHtml(hits);
  box.querySelectorAll("[data-card-name]").forEach((b) => {
    b.onclick = () => applyPickedCard({ id: b.dataset.cardId, name: b.dataset.cardName });
  });
}

function cardCount(d) {
  if (!d) return 0;
  if (Number.isFinite(d.count)) return d.count;
  return (d.cards || []).length;
}

function ruleSets() {
  return decksMatchingRule(currentRule(), { includeSpare: false });
}

function fillViewSet(preferred) {
  const sel = $("#viewSet");
  if (!sel) return;
  const keep = preferred || sel.value;
  const lists = ruleSets();
  sel.innerHTML = lists.map((d) =>
    `<option value="${esc(d.id)}">${esc(d.name)} (${cardCount(d)})</option>`
  ).join("");
  if (keep && [...sel.options].some((o) => o.value === keep)) sel.value = keep;
  else if (lists[0]) sel.value = lists[0].id;
  $("#openAddCard")?.toggleAttribute("disabled", !sel.value);
}

function fillAddToSet(preferred) {
  const sel = $("#addToSet");
  if (!sel) return;
  const keep = pickerTarget?.deckId || preferred || sel.value;
  const lists = ruleSets();
  sel.innerHTML = `<option value="__new__">New set…</option>`
    + lists.map((d) => `<option value="${esc(d.id)}">${esc(d.name)} (${cardCount(d)})</option>`).join("");
  if (keep && [...sel.options].some((o) => o.value === keep)) sel.value = keep;
  else if (lists[0]) sel.value = lists[0].id;
  else sel.value = "__new__";
  sel.disabled = Boolean(pickerTarget?.deckId);
  syncNewSetWrap();
  if (pickerTarget?.deckId && sel.value !== pickerTarget.deckId) closeCardSheet();
}

function syncNewSetWrap() {
  const wrap = $("#newSetWrap");
  if (!wrap) return;
  const locked = Boolean(pickerTarget?.deckId);
  wrap.classList.toggle("hidden", locked || $("#addToSet")?.value !== "__new__");
}

function parkCardsPanel(host) {
  const panel = $("#findPanel");
  if (panel && host && panel.parentElement !== host) host.appendChild(panel);
}

function paintCardPickerChrome() {
  const deck = pickerTarget?.deckId
    ? state.decks.find((d) => d.id === pickerTarget.deckId)
    : null;
  const current = deck && pickerTarget?.kind === "replace"
    ? deck.cards?.[pickerTarget.index]
    : null;
  const replacing = pickerTarget?.kind === "replace";
  const adding = pickerTarget?.kind === "add";
  $("#findPanel")?.classList.toggle("replacing", replacing);
  $("#cancelReplace")?.classList.toggle("hidden", !replacing);
  if ($("#addCard")) $("#addCard").textContent = replacing ? "Replace card" : "Add to set";
  if ($("#cardSheetTitle")) {
    $("#cardSheetTitle").textContent = replacing
      ? (current ? `Replace ${current.name}` : "Replace a card")
      : (adding ? `Add to ${deck?.name || "this set"}` : "Add a card");
  }
  if ($("#findHint")) {
    if (replacing) {
      $("#findHint").textContent = current
        ? `Replacing ${current.name} in ${deck?.name || "this set"}. Search or scan, then tap a card.`
        : "Search or scan, then tap a card to replace.";
    } else if (adding) {
      $("#findHint").textContent = `Search or scan, then tap + to add a card to ${deck?.name || "this set"}.`;
    } else {
      $("#findHint").textContent = "Search a name or photograph cards. Tap + to add it to a set.";
    }
  }
  syncNewSetWrap();
}

let cardSheetOpener = null;

function openCardPicker(target) {
  pickerTarget = { ...target, seq: ++pickerSeq };
  const seq = pickerTarget.seq;
  if (target?.deckId) fillAddToSet(target.deckId);
  else fillAddToSet($("#addToSet")?.value);
  if (pickerTarget?.seq !== seq) return;
  if ($("#cardSheet")?.classList.contains("hidden")) {
    cardSheetOpener = document.activeElement;
  }
  parkCardsPanel($("#cardSheetHost"));
  $("#cardSheet")?.classList.remove("hidden");
  document.body.classList.add("card-sheet-open");
  paintCardPickerChrome();
  $("#addName")?.focus();
}

function closeCardSheet() {
  const sheet = $("#cardSheet");
  const wasOpen = Boolean(sheet && !sheet.classList.contains("hidden"));
  const focusInSheet = Boolean(sheet && document.activeElement && sheet.contains(document.activeElement));
  pickerTarget = null;
  $("#cardSheet")?.classList.add("hidden");
  document.body.classList.remove("card-sheet-open");
  const sel = $("#addToSet");
  if (sel) sel.disabled = false;
  parkCardsPanel($("#cardsHost"));
  paintCardPickerChrome();
  if (wasOpen && focusInSheet && cardSheetOpener && typeof cardSheetOpener.focus === "function") {
    cardSheetOpener.focus();
  }
  cardSheetOpener = null;
  return wasOpen;
}

function startReplace(deckId, index) {
  fillViewSet(deckId);
  openCardPicker({ kind: "replace", deckId, index });
}

function startAddCard(deckId) {
  if (!deckId) {
    toast("Pick a set first.", "bad");
    return;
  }
  fillViewSet(deckId);
  openCardPicker({ kind: "add", deckId });
}

async function takeCard(card, session = pickerTarget) {
  const seq = session?.seq;
  if (session?.kind === "replace") {
    await replaceDeckCard(session.deckId, session.index, card);
    if (pickerTarget?.seq === seq) closeCardSheet();
    toast(`Replaced with ${card.name}`);
    return;
  }
  await addCardsToSet([card], session);
  if (session && pickerTarget?.seq === seq) closeCardSheet();
}

async function addCardsToSet(cards, session = pickerTarget) {
  const named = (cards || []).filter((c) => c && c.name && c.name !== "Unknown");
  if (!named.length) throw new Error("No named cards to add");
  if (session?.kind === "replace") {
    await takeCard(named[0], session);
    return;
  }
  const sel = $("#addToSet")?.value;
  if (!sel || sel === "__new__") {
    const name = ($("#newSetName")?.value || "New set").trim() || "New set";
    const saved = await api("/api/decks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, cards: named, source: named.length > 1 ? "scan" : "search", rule_presets: [currentRule()] }),
    });
    state.decks = await api("/api/decks");
    fillAddToSet(saved.id);
    fillViewSet(saved.id);
    renderDecks();
    toast(`Started ${saved.name} with ${named.length === 1 ? named[0].name : named.length + " cards"}`);
    return;
  }
  const deck = state.decks.find((d) => d.id === sel);
  if (!deck) throw new Error("Pick a set first");
  const next = (deck.cards || []).concat(named);
  const saved = await api(`/api/decks/${encodeURIComponent(deck.id)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: deck.name, cards: next, source: deck.source }),
  });
  const i = state.decks.findIndex((d) => d.id === deck.id);
  if (i >= 0) state.decks[i] = saved;
  fillAddToSet(saved.id);
  fillViewSet(saved.id);
  renderDecks();
  toast(`Added ${named.length === 1 ? named[0].name : named.length + " cards"} to ${saved.name}`);
}

function foldName(s) {
  return String(s || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function selectedSearchHit() {
  const typed = $("#addName")?.value.trim() || "";
  const bound = foldName($("#addHits")?.dataset.query || "");
  const rows = $$("#addHits [data-card-name]").map((b) => ({
    id: b.dataset.cardId || "",
    name: b.dataset.cardName || "",
  })).filter((h) => h.name);
  const folded = foldName(typed);
  const live = Boolean(folded && bound === folded);
  if (live) {
    const exact = rows.find((h) => foldName(h.name) === folded);
    if (exact) return exact;
    if (rows[0]) return rows[0];
  }
  if (typed) return { name: typed };
  return null;
}

let addBusy = false;
async function applyPickedCard(hit) {
  if (!hit || !hit.name || addBusy) return;
  const session = pickerTarget;
  addBusy = true;
  $("#addCard")?.setAttribute("disabled", "true");
  try {
    await takeCard(await resolvePick(hit), session);
  } catch (err) {
    toast(err.message, "bad");
  } finally {
    addBusy = false;
    $("#addCard")?.removeAttribute("disabled");
  }
}

async function replaceDeckCard(deckId, index, card) {
  const deck = state.decks.find((d) => d.id === deckId);
  if (!deck || !deck.cards || index < 0 || index >= deck.cards.length) {
    throw new Error("Card not found in that set");
  }
  const cards = deck.cards.slice();
  cards[index] = card;
  const saved = await api(`/api/decks/${encodeURIComponent(deckId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: deck.name, cards, source: deck.source }),
  });
  const i = state.decks.findIndex((d) => d.id === deckId);
  if (i >= 0) state.decks[i] = saved;
  renderDecks();
}

function selectedSet() {
  const id = $("#viewSet")?.value;
  if (!id) return null;
  return (state.decks || []).find((d) => d.id === id) || null;
}

function renderDecks() {
  const d = selectedSet();
  const box = $("#deckList");
  if (!box) return;
  if (!d) {
    box.innerHTML = `<div class="panel"><p class="tiny">No set for this rule yet. Open Cards and start a new set, or tap Add a card after you have one.</p></div>`;
    return;
  }
  const have = deckRulePresets(d);
  const ruleNames = have.map((k) => (k === "c" ? "No Pokémon energy" : "Pokémon = energy")).join(" · ");
  box.innerHTML = `
    <div class="panel">
      <div class="list-item">
        <div>
          <b>${esc(d.name)}</b>
          <div class="tiny">${cardCount(d)} cards · ${esc(ruleNames)} · ${d.kind === "spare" ? "leftover pile" : esc(d.id)}</div>
          ${ruleToggleHtml(d)}
          <div class="type-mix" style="justify-content:flex-start;margin-top:6px">${mixHtml(d.cards)}</div>
        </div>
        ${String(d.id || "").startsWith("seed-") ? "" : `<button class="danger" type="button" data-delete-set="${esc(d.id)}">Delete set</button>`}
      </div>
      <div class="grid">
        ${(d.cards || []).map((c, i) => cardTile(c, { deckId: d.id, index: i })).join("")}
      </div>
    </div>`;
  bindZoom(box);
  bindReplace(box);
  box.querySelectorAll("[data-delete-set]").forEach((btn) => {
    btn.onclick = () => deleteSelectedSet(btn.dataset.deleteSet);
  });
  box.querySelectorAll("[data-rule-key]").forEach((input) => {
    input.onchange = () => toggleDeckRule(d.id, input.dataset.ruleKey, input.checked);
  });
}

function ruleToggleHtml(d) {
  const have = new Set(deckRulePresets(d));
  return `<div class="rule-tags" role="group" aria-label="Rules this set follows">${ruleChoices().map((p) => `
    <label class="rule-tag"><input type="checkbox" data-rule-key="${esc(p.preset)}" ${have.has(p.preset) ? "checked" : ""} /> ${esc(p.label)}</label>
  `).join("")}</div>`;
}

async function toggleDeckRule(deckId, key, on) {
  const deck = (state.decks || []).find((d) => d.id === deckId);
  if (!deck) return;
  const have = new Set(deckRulePresets(deck));
  if (on) have.add(key);
  else have.delete(key);
  const next = ruleChoices().map((p) => p.preset).filter((k) => have.has(k));
  if (!next.length) {
    toast("Keep at least one rule.", "bad");
    renderDecks();
    return;
  }
  try {
    const saved = await api(`/api/decks/${encodeURIComponent(deckId)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: deck.name, source: deck.source, rule_presets: next }),
    });
    const i = state.decks.findIndex((d) => d.id === deckId);
    if (i >= 0) state.decks[i] = saved;
    fillAddToSet(saved.id);
    fillViewSet(saved.id);
    fillFight();
    renderDecks();
    if (!deckRulePresets(saved).includes(currentRule())) {
      toast(`${saved.name} is no longer under this rule`);
    }
  } catch (err) {
    toast(err.message, "bad");
    renderDecks();
  }
}

async function deleteSelectedSet(deckId) {
  const deck = (state.decks || []).find((d) => d.id === deckId);
  if (!deck) return;
  if (String(deckId).startsWith("seed-")) {
    toast("Starter sets cannot be deleted.", "bad");
    return;
  }
  if (!window.confirm(`Delete ${deck.name}? This cannot be undone.`)) return;
  try {
    await api(`/api/decks/${encodeURIComponent(deckId)}`, { method: "DELETE" });
  } catch (err) {
    toast(err.message, "bad");
    return;
  }
  state.decks = state.decks.filter((d) => d.id !== deckId);
  closeCardSheet();
  fillAddToSet();
  fillViewSet();
  fillFight();
  renderDecks();
  toast(`${deck.name} deleted`);
}

$("#addCard").onclick = async () => {
  const hit = selectedSearchHit();
  if (!hit) return toast("Search a card first.", "bad");
  await applyPickedCard(hit);
};

$("#addName")?.addEventListener("input", () => {
  clearTimeout(cardSearchTimer);
  const box = $("#addHits");
  if (box) box.dataset.query = "";
  const q = $("#addName").value.trim();
  cardSearchTimer = setTimeout(() => runCardSearch(q), 120);
});
$("#addName")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    $("#addCard")?.click();
  }
});
$("#addToSet")?.addEventListener("change", () => {
  syncNewSetWrap();
});
$("#viewSet")?.addEventListener("change", () => renderDecks());
$("#openAddCard")?.addEventListener("click", () => startAddCard($("#viewSet")?.value));
$("#closeCardSheet")?.addEventListener("click", () => closeCardSheet());
$("#cardSheet")?.addEventListener("click", (e) => {
  if (e.target.id === "cardSheet") closeCardSheet();
});
$("#cancelReplace")?.addEventListener("click", () => closeCardSheet());
$("#findScan")?.addEventListener("change", async (e) => {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file) return;
  setBusy(true, "Reading the photo…", true);
  try {
    const fd = new FormData();
    fd.append("file", file);
    const result = await api("/api/recognize", { method: "POST", body: fd });
    const cards = (result.cards || []).filter((c) => c.name && c.name !== "Unknown");
    if (!cards.length) throw new Error("Could not read that photo. Search by name instead.");
    const session = pickerTarget;
    await addCardsToSet(cards, session);
    if (session && pickerTarget?.seq === session.seq) closeCardSheet();
  } catch (err) {
    toast(err.message, "bad");
  } finally {
    setBusy(false);
  }
});

function pct(n) {
  return Math.round((n || 0) * 100);
}

function winnerOf(rec) {
  const r = rec.results || {};
  if ((r.win_rate_a || 0) > (r.win_rate_b || 0) + 0.002) return "a";
  if ((r.win_rate_b || 0) > (r.win_rate_a || 0) + 0.002) return "b";
  return "tie";
}

function resultPanel(rec, opts = {}) {
  const r = rec.results || {};
  const a = pct(r.win_rate_a);
  const b = pct(r.win_rate_b);
  const t = pct(r.tie_rate);
  const learn = rec.learning || {};
  const win = winnerOf(rec);
  const aName = rec.decks?.a?.name || "A";
  const bName = rec.decks?.b?.name || "B";
  const banner = win === "tie"
    ? "Too close to call"
    : `${esc(win === "a" ? aName : bName)} takes the Cup`;
  const combo = learn.combo
    ? `<p class="ok">Pikachu paralyzed Dondozo in ${((learn.combo.p_games_with_success ?? learn.combo.p_landed_per_game) * 100).toFixed(1)}% of games.</p>`
    : "";
  const first = r.win_rate_a_going_first != null
    ? `<div class="split">
        <div><div class="tiny">A going first</div><b>${pct(r.win_rate_a_going_first)}%</b></div>
        <div><div class="tiny">A going second</div><b>${pct(r.win_rate_a_going_second)}%</b></div>
      </div>`
    : "";
  const hand = rec.method?.rules?.opening_hand || state.rules?.opening_hand || 7;
  const odds = r.opening_probabilities
    ? Object.entries(r.opening_probabilities).map(([name, sides]) =>
      `<div class="tiny">${esc(name)} in opening ${hand} — A ${(((sides.deck_a && sides.deck_a.p_at_least_one) || 0) * 100).toFixed(0)}% · B ${(((sides.deck_b && sides.deck_b.p_at_least_one) || 0) * 100).toFixed(0)}%</div>`
    ).join("")
    : "";
  const replay = opts.replayHtml || "";
  return `
    <div class="panel">
      <div class="banner">${banner}</div>
      <div class="stat">${a}% / ${b}%</div>
      <p>A wins vs B wins · ${rec.method?.games?.toLocaleString()} games · ${rec.elapsed_seconds}s · seed ${rec.method?.seed}</p>
      <div class="bar"><div class="a" style="width:${a}%"></div><div class="b" style="width:${b}%"></div><div class="t" style="width:${t}%"></div></div>
      ${first}
      <p><b>Method</b><br>${esc(rec.method?.how || "")}</p>
      <p><b>Strategies</b><br>A: ${esc(rec.strategies?.a?.name)} — ${esc(rec.strategies?.a?.description)}<br>
      B: ${esc(rec.strategies?.b?.name)} — ${esc(rec.strategies?.b?.description)}</p>
      <p><b>What the AI learned</b></p>
      ${(learn.insights || []).map((i) => `<div class="insight">${esc(i)}</div>`).join("")}
      ${combo}
      ${odds}
      <p class="tiny">Lab id ${esc(rec.id)}</p>
      ${replay}
    </div>`;
}

function beginStadiumRun(hint) {
  stopReplay();
  resetArenaResult();
  if ($("#arenaHint") && hint) $("#arenaHint").textContent = hint;
}

function applyArenaResult(rec) {
  const stage = $("#arenaStage");
  if (!stage) return;
  const win = winnerOf(rec);
  const aName = rec.decks?.a?.name || $("#nameA")?.textContent || "A";
  const bName = rec.decks?.b?.name || $("#nameB")?.textContent || "B";
  stage.classList.remove("winner-a", "winner-b", "winner-tie");
  stage.classList.add(`winner-${win}`);
  paintPrizes(win);
  if ($("#vsBadge")) $("#vsBadge").textContent = win === "tie" ? "TIE" : "VS";
  if ($("#arenaHint")) {
    if (win === "tie") $("#arenaHint").textContent = "Even match";
    else if (win === "a") $("#arenaHint").textContent = `${aName} takes it`;
    else $("#arenaHint").textContent = `${bName} takes it`;
  }
  if (win !== "tie") {
    ping("win");
    burstConfetti();
  }
}

function replayHtml(rec, boxId) {
  const log = rec.sample_games?.[0]?.log || [];
  if (!log.length) return "";
  const sample = rec.sample_games[0];
  return `<div class="replay-wrap">
    <div class="tiny">Sample game · ${esc(sample.turns)} turns · winner ${esc(sample.winner)} · ${esc(sample.reason || "")}</div>
    <div class="replay" id="${boxId}">${log.map((line, i) =>
      `<div class="log-line ${classifyLog(line)}${i === 0 ? " current" : ""}">${esc(line)}</div>`
    ).join("")}</div>
    <div class="replay-controls">
      <button class="secondary" type="button" data-replay="${boxId}">Play log</button>
    </div>
  </div>`;
}

let replayTimer = 0;
let replayGen = 0;
function stopReplay() {
  replayGen += 1;
  if (replayTimer) clearTimeout(replayTimer);
  replayTimer = 0;
}
function playLog(boxId) {
  const box = document.getElementById(boxId);
  if (!box) return;
  const gen = ++replayGen;
  if (replayTimer) clearTimeout(replayTimer);
  const lines = [...box.querySelectorAll(".log-line")];
  let i = 0;
  const step = () => {
    if (gen !== replayGen) return;
    lines.forEach((el, idx) => el.classList.toggle("current", idx === i));
    const kind = classifyLog(lines[i]?.textContent);
    if (kind === "ko") ping("ko");
    else if (kind === "attack") ping("click");
    lines[i]?.scrollIntoView({ block: "nearest" });
    i += 1;
    if (i < lines.length) replayTimer = setTimeout(step, REDUCE ? 0 : 520);
  };
  step();
}

function bindReplay(root, boxId) {
  root?.querySelector("[data-replay]")?.addEventListener("click", () => playLog(boxId));
}

function burstConfetti() {
  const canvas = $("#confetti");
  if (!canvas || REDUCE) return;
  canvas.classList.remove("hidden");
  const ctx = canvas.getContext("2d");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const bits = Array.from({ length: 80 }, () => ({
    x: Math.random() * canvas.width,
    y: -20 - Math.random() * 80,
    r: 3 + Math.random() * 4,
    vx: -1.4 + Math.random() * 2.8,
    vy: 2 + Math.random() * 3.2,
    color: ["#ffcb05", "#ee1515", "#3d7dca", "#3dd68c", "#c77dff"][Math.floor(Math.random() * 5)],
  }));
  let frames = 0;
  const tick = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    bits.forEach((p) => {
      p.x += p.vx; p.y += p.vy; p.vy += 0.05;
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x, p.y, p.r, p.r * 1.6);
    });
    frames += 1;
    if (frames < 90) requestAnimationFrame(tick);
    else canvas.classList.add("hidden");
  };
  tick();
}

function simPayload(games) {
  return {
    deck_a_id: $("#deckA").value,
    deck_b_id: $("#deckB").value,
    strategy_a: $("#stratA").value,
    strategy_b: $("#stratB").value,
    rule_preset: $("#rulePreset")?.value || "b",
    games,
    question: $("#simQuestion").value,
  };
}

$("#runSim").onclick = async () => {
  beginStadiumRun("Shuffling both sets…");
  $("#simOut").innerHTML = `<div class="panel">Running ${$("#games").value} games…</div>`;
  setBusy(true, `Running ${Number($("#games").value).toLocaleString()} Family Cup games…`, true);
  try {
    const rec = await api("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(simPayload(+$("#games").value)),
    });
    $("#simOut").innerHTML = resultPanel(rec, { replayHtml: replayHtml(rec, "fightReplay") });
    bindReplay($("#simOut"), "fightReplay");
    applyArenaResult(rec);
  } catch (err) {
    resetArenaResult();
    if ($("#arenaHint")) $("#arenaHint").textContent = "Simulation failed";
    $("#simOut").innerHTML = `<div class="panel">${esc(err.message)}</div>`;
  } finally {
    setBusy(false);
  }
};

$("#watchOne").onclick = async () => {
  beginStadiumRun("Playing one honest game…");
  $("#simOut").innerHTML = `<div class="panel">Playing one honest game…</div>`;
  setBusy(true, "Playing one Family Cup game on the stadium floor…", true);
  try {
    const rec = await api("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(simPayload(1)),
    });
    $("#simOut").innerHTML = resultPanel(rec, { replayHtml: replayHtml(rec, "watchReplay") });
    bindReplay($("#simOut"), "watchReplay");
    applyArenaResult(rec);
    playLog("watchReplay");
  } catch (err) {
    resetArenaResult();
    if ($("#arenaHint")) $("#arenaHint").textContent = "Simulation failed";
    $("#simOut").innerHTML = `<div class="panel">${esc(err.message)}</div>`;
  } finally {
    setBusy(false);
  }
};

$("#runTrades").onclick = async () => {
  beginStadiumRun("Looking for win-win trades");
  $("#simOut").innerHTML = `<div class="panel">Searching win-win trades…</div>`;
  setBusy(true, "Trying 1-for-1 swaps that help both sets…", true);
  try {
    const rec = await api("/api/trades", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        deck_a_id: $("#deckA").value,
        deck_b_id: $("#deckB").value,
      }),
    });
    const rows = (rec.recommendations || []).map((t) =>
      `<div class="list-item"><div><b>${esc(t.give_a)} ⇄ ${esc(t.give_b)}</b><div class="tiny">${esc(t.why_a)}. ${esc(t.why_b)}</div></div><div>${Math.round(t.win_rate_a_after * 100)}% A</div></div>`
    ).join("");
    $("#simOut").innerHTML = `<div class="panel"><p>${esc(rec.method)}</p><p>A needs ${esc((rec.needs_a || []).join(", ") || "—")}. B needs ${esc((rec.needs_b || []).join(", ") || "—")}.</p>${rows || "No helpful 1-for-1 found."}</div>`;
  } catch (err) {
    $("#simOut").innerHTML = `<div class="panel">${esc(err.message)}</div>`;
  } finally {
    setBusy(false);
  }
};

async function sendChat() {
  const message = $("#chatInput").value.trim();
  if (!message || sendChat.busy) return;
  const fromVoice = !!sendChat.fromVoice;
  sendChat.fromVoice = false;
  if (!fromVoice) voice.loop = false;
  stopVoiceListen();
  sendChat.busy = true;
  sendChat.streaming = true;
  $("#sendChat").disabled = true;
  showThread();
  $("#chatLog").insertAdjacentHTML("beforeend", `<div class="msg user">${md(message)}</div>`);
  $("#chatInput").value = "";
  const bot = document.createElement("div");
  bot.className = "msg bot live";
  const trace = document.createElement("div");
  trace.className = "tiny trace";
  const body = document.createElement("div");
  body.innerHTML = "正在想… / Thinking…";
  bot.appendChild(trace);
  bot.appendChild(body);
  $("#chatLog").appendChild(bot);
  $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
  setBusy(true, "正在想… / Thinking…");
  let answer = "";
  try {
    const res = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, chat_id: state.chatId, history: state.history, language: state.chatLang }),
    });
    if (res.status === 401) {
      clearClientSession();
      showAuthGate();
      shrinkAgent({ focusLauncher: false });
      throw new Error("Sign in required");
    }
    if (!res.ok || !res.body) throw new Error(await res.text());
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || "";
      for (const part of parts) {
        for (const line of part.split("\n")) {
          if (!line.startsWith("data: ")) continue;
          const event = JSON.parse(line.slice(6));
          if (event.type === "status" && event.text) {
            trace.textContent = event.text;
            if ($("#busyLine")) $("#busyLine").textContent = event.text;
          } else if (event.type === "tool") {
            const name = event.tool || event.name || "tool";
            trace.textContent = `${name} ${event.status || ""}`.trim();
          } else if (event.type === "text" && event.text) {
            answer += event.text;
            body.innerHTML = md(answer);
          } else if (event.type === "done") {
            state.chatId = event.chat_id;
            state.history = event.messages;
            rememberChat(event.chat_id);
            answer = event.answer || answer;
            body.innerHTML = md(answer);
            $("#chatTitle").textContent = threadTitle(event.messages);
            if (event.coach && event.coach !== "cursor") {
              trace.textContent = event.coach === "local" ? "Local coach" : event.coach;
            } else {
              trace.remove();
            }
          }
        }
      }
      $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
    }
    bot.classList.remove("live");
  } catch (err) {
    body.innerHTML = md(String(err.message || err));
    bot.classList.remove("live");
  } finally {
    sendChat.streaming = false;
    setBusy(false);
    renderChatThreads();
    const pending = sendChat.pending;
    sendChat.pending = null;
    const spoken = answer || body.textContent || "";
    try {
      if (chatViewOpen() && !sendChat.muteSpeak) await speakReply(spoken);
    } finally {
      sendChat.muteSpeak = false;
      sendChat.busy = false;
      if ($("#sendChat")) $("#sendChat").disabled = false;
      if (pending?.message) {
        $("#chatInput").value = pending.message;
        sendChat.fromVoice = !!pending.fromVoice;
        sendChat();
      } else if (voice.loop && fromVoice && chatViewOpen() && !voice.rec) {
        startVoiceListen();
      }
    }
  }
}

function rememberChat(chatId) {
  try {
    if (chatId) localStorage.setItem(CHAT_STORE, chatId);
    else localStorage.removeItem(CHAT_STORE);
  } catch {
    /* private mode */
  }
}

function threadTitle(messages) {
  const first = (messages || []).find((m) => m.role === "user" && m.content);
  const text = (first?.content || (state.chatLang === "zh" ? "新对话" : "New chat")).replace(/\s+/g, " ").trim();
  return text.length > 60 ? `${text.slice(0, 57)}…` : text;
}

function renderChatLog(messages) {
  $("#chatLog").innerHTML = (messages || [])
    .filter((m) => m.role === "user" || m.role === "assistant")
    .map((m) => `<div class="msg ${m.role === "user" ? "user" : "bot"}">${md(m.content || "")}</div>`)
    .join("");
  $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
}

function showThread() {
  state.chatMode = "thread";
  $("#chatThreads").classList.add("hidden");
  $("#chatThread").classList.remove("hidden");
}

function showThreadList() {
  state.chatMode = "list";
  $("#chatThread").classList.add("hidden");
  $("#chatThreads").classList.remove("hidden");
  renderChatThreads();
}

function startNewChat() {
  state.chatId = null;
  state.history = [];
  rememberChat(null);
  $("#chatTitle").textContent = state.chatLang === "zh" ? "新对话" : "New chat";
  $("#chatLog").innerHTML = `<div class="msg bot welcome">${md(CHAT_WELCOME)}</div>`;
  $("#chatInput").value = "";
  showThread();
}

async function openThread(chatId) {
  const chat = await api(`/api/chats/${chatId}`);
  state.chatId = chat.id;
  state.history = chat.messages || [];
  rememberChat(chat.id);
  $("#chatTitle").textContent = chat.title || threadTitle(chat.messages);
  renderChatLog(chat.messages);
  showThread();
}

async function renderChatThreads() {
  const q = ($("#chatSearch")?.value || "").trim();
  const rows = await api(`/api/chats${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  const box = $("#chatThreads");
  if (!rows.length) {
    box.innerHTML = `<div class="panel"><p class="tiny">${q ? "No threads match. / 没有找到对话。" : "No threads yet. Tap New. / 还没有对话，点「新对话」。"}</p></div>`;
    return;
  }
  box.innerHTML = rows.map((row) => `
    <div class="panel thread${row.id === state.chatId ? " active" : ""}" data-open="${esc(row.id)}">
      <div class="list-item">
        <div>
          <b>${esc(row.title)}</b>
          <div class="tiny">${esc(row.preview || "")}</div>
          <div class="tiny">${esc(when(row.updated_at))} · ${row.turns || 0} turn${row.turns === 1 ? "" : "s"}</div>
        </div>
        <button class="ghost" data-del="${esc(row.id)}" type="button">✕</button>
      </div>
    </div>`).join("");
  box.querySelectorAll("[data-open]").forEach((el) => {
    el.onclick = (ev) => {
      if (ev.target.closest("[data-del]")) return;
      openThread(el.dataset.open).catch((err) => { box.innerHTML = `<div class="panel">${esc(err.message)}</div>`; });
    };
  });
  box.querySelectorAll("[data-del]").forEach((btn) => {
    btn.onclick = async (ev) => {
      ev.stopPropagation();
      await api(`/api/chats/${btn.dataset.del}`, { method: "DELETE" });
      if (state.chatId === btn.dataset.del) {
        state.chatId = null;
        state.history = [];
        rememberChat(null);
      }
      showThreadList();
    };
  });
}

async function renderChat() {
  if (state.chatMode === "thread") {
    showThread();
    return;
  }
  if (state.chatOpened) {
    showThreadList();
    return;
  }
  state.chatOpened = true;
  let remembered = null;
  try { remembered = localStorage.getItem(CHAT_STORE); } catch { remembered = null; }
  if (!state.chatId && remembered) {
    try {
      await openThread(remembered);
      return;
    } catch {
      rememberChat(null);
    }
  }
  startNewChat();
}

$("#sendChat").onclick = sendChat;
$("#newChat").onclick = () => {
  startNewChat();
  $("#chatInput").focus();
};
$("#backToThreads").onclick = () => showThreadList();
$("#chatLangZh").onclick = () => setChatLang("zh");
$("#chatLangEn").onclick = () => setChatLang("en");
$("#chatSpeak").onclick = toggleSpeakReplies;
$("#chatMic").onclick = toggleChatMic;
$("#cubLauncher").onclick = () => openAgent();
$("#agentShrink").onclick = () => shrinkAgent();
$("#agentFull").onclick = () => toggleAgentFull();
if (ttsSupported()) {
  window.speechSynthesis.onvoiceschanged = () => {};
}
let searchTimer = 0;
$("#chatSearch").oninput = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    showThreadList();
  }, 180);
};
$("#chatInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChat();
  }
});

async function renderLab() {
  const rows = await api("/api/simulations");
  $("#labList").innerHTML = rows.map((r) => `
    <div class="panel">
      <div class="list-item">
        <div><b>${esc(r.question || "Match simulation")}</b>
        <div class="tiny">${esc(r.created_at)} · ${r.games} games · A win ${((r.win_rate_a || 0) * 100).toFixed(1)}%</div>
        <div class="tiny">${esc((r.learning || []).join(" · "))}</div></div>
        <button class="secondary" data-lab="${esc(r.id)}">Open</button>
      </div>
    </div>`).join("") || `<div class="panel">No runs yet. Fight a matchup and it will land here.</div>`;
  $$("[data-lab]").forEach((b) => b.onclick = async () => {
    const rec = await api(`/api/simulations/${b.dataset.lab}`);
    $("#labDetail").innerHTML = resultPanel(rec, { replayHtml: replayHtml(rec, "labReplay") })
      + `<div class="panel"><b>Sample game</b><p class="tiny">${(rec.sample_games?.[0]?.log || []).map((l) => esc(l)).join("<br>")}</p></div>`;
    bindReplay($("#labDetail"), "labReplay");
  });
}

let lightboxOpener = null;
function openLightbox(src, name) {
  lightboxOpener = document.activeElement;
  $("#lightboxImg").src = src;
  $("#lightboxImg").alt = name;
  $("#lightboxCap").textContent = name;
  $("#lightbox").classList.remove("hidden");
  $("#lightboxClose")?.focus();
}
function closeLightbox() {
  if ($("#lightbox").classList.contains("hidden")) return;
  $("#lightbox").classList.add("hidden");
  if (lightboxOpener && typeof lightboxOpener.focus === "function") lightboxOpener.focus();
  lightboxOpener = null;
}
$("#lightboxClose").onclick = () => closeLightbox();
$("#lightbox").addEventListener("click", (e) => {
  if (e.target.id === "lightbox") closeLightbox();
});

["deckA", "deckB", "stratA", "stratB", "rulePreset"].forEach((id) => {
  $(`#${id}`)?.addEventListener("change", () => {
    if (id === "rulePreset") {
      rememberRule($("#rulePreset").value);
      const preset = state.rulePresets?.find((p) => p.preset === $("#rulePreset").value);
      if (preset) paintRules(preset);
      fillFight();
      fillAddToSet($("#addToSet")?.value);
      fillViewSet($("#viewSet")?.value);
      renderDecks();
    }
    resetArenaResult();
    paintArena();
  });
});

$("#sfxToggle").onclick = () => {
  sfx.on = !sfx.on;
  try { localStorage.setItem(SFX_STORE, sfx.on ? "1" : "0"); } catch { /* private mode */ }
  paintSfx();
  ping("click");
};

let brandHits = 0;
$("#brandTap").onclick = () => {
  brandHits += 1;
  if (brandHits < 5) return;
  brandHits = 0;
  document.body.classList.toggle("shiny");
  try {
    localStorage.setItem(SHINY_STORE, document.body.classList.contains("shiny") ? "1" : "0");
  } catch { /* private mode */ }
  toast(document.body.classList.contains("shiny") ? "Shiny mode" : "Stadium lights normal");
};

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    if (!$("#cardSheet")?.classList.contains("hidden")) {
      closeCardSheet();
      return;
    }
    const lightboxOpen = !$("#lightbox")?.classList.contains("hidden");
    closeLightbox();
    if (lightboxOpen) return;
    if (document.body.classList.contains("agent-full")) {
      document.body.classList.remove("agent-full");
      paintAgentChrome();
    } else if (document.body.classList.contains("agent-open")) {
      shrinkAgent();
    }
    return;
  }
  if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
  const map = { 1: "cards", 2: "decks", 3: "fight", 4: "lab" };
  if (map[e.key]) show(map[e.key]);
});

$$(".nav button").forEach((b) => b.onclick = () => show(b.dataset.view));
boot().catch((err) => { $("#aiPill").textContent = "Error"; console.error(err); });
