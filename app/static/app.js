const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];
let state = { decks: [], strategies: [], scanCards: [], scanCrops: [], chatId: null, history: [] };

const CHIPS = [
  "What is the probability Dondozo appears in the first 7 cards?",
  "If I use Pikachu to paralyze Dondozo, how often can I pull that off?",
  "Run 10,000 games. What strategy won, and what did you learn?",
  "Which cards should we trade so both sets get stronger?",
];

async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function show(view) {
  $$("main > section").forEach((s) => s.classList.add("hidden"));
  $(`#view-${view}`).classList.remove("hidden");
  $$(".nav button").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  if (view === "decks") renderDecks();
  if (view === "fight") fillFight();
  if (view === "lab") renderLab();
}

function md(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
    .replace(/\n/g, "<br>");
}

async function boot() {
  const health = await api("/api/health");
  $("#aiPill").textContent = health.ai.configured ? `${health.ai.provider} · ${health.ai.model}` : "Local coach";
  state.decks = await api("/api/decks");
  state.strategies = await api("/api/strategies");
  CHIPS.forEach((q) => {
    const b = document.createElement("button");
    b.textContent = q;
    b.onclick = () => { show("chat"); $("#chatInput").value = q; sendChat(); };
    $("#chips").appendChild(b);
  });
  fillFight();
  renderEditor();
}

function fillFight() {
  for (const id of ["deckA", "deckB"]) {
    const sel = $(`#${id}`);
    sel.innerHTML = state.decks.map((d) => `<option value="${d.id}">${d.name} (${d.count})</option>`).join("");
  }
  if (state.decks[1]) $("#deckB").value = state.decks[1].id;
  for (const id of ["stratA", "stratB"]) {
    $(`#${id}`).innerHTML = state.strategies.map((s) => `<option value="${s.name}">${s.name}</option>`).join("");
  }
  if ([...$("#stratA").options].some((o) => o.value === "thrifty")) $("#stratA").value = "thrifty";
  if ([...$("#stratB").options].some((o) => o.value === "shock")) $("#stratB").value = "shock";
}

function renderEditor() {
  const box = $("#editor");
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
      <input data-crop="${i}" value="${shown.replaceAll('"', "&quot;")}" placeholder="Card name">
      <div class="tiny">${Math.round(c.confidence || 0)}%${c.needs_review ? " · check" : ""}</div>
      <button class="ghost" data-drop="${i}" type="button">✕</button>
    </div>`;
  }).join("")}</div>` : "";
  box.innerHTML = cropHtml + (cropHtml ? "" : state.scanCards.map((c, i) => `
    <div class="editor-row">
      <div class="grow"><b>${c.name}</b><div class="tiny">${c.category} ${c.stage || ""} ${c.hp ? c.hp + " HP" : ""}</div></div>
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
    alert(err.message);
  }
}

function renderDecks() {
  $("#deckList").innerHTML = state.decks.map((d) => `
    <div class="panel">
      <div class="list-item">
        <div><b>${d.name}</b><div class="tiny">${d.count} cards · ${d.id}</div></div>
      </div>
      <div class="grid">
        ${d.cards.map((c) => `
          <div class="card-tile">
            ${c.image ? `<img src="${c.image}" alt="${c.name}">` : ""}
            <div class="meta"><b>${c.name}</b><span>${c.category} ${c.hp ? c.hp + " HP" : ""}</span></div>
          </div>`).join("")}
      </div>
    </div>`).join("");
}

async function recognizeFile(file) {
  $("#preview").src = URL.createObjectURL(file);
  $("#preview").classList.remove("hidden");
  const fd = new FormData();
  fd.append("file", file);
  document.body.classList.add("busy");
  try {
    const result = await api("/api/recognize", { method: "POST", body: fd });
    state.scanCrops = (result.crops || []).map((c, i) => ({
      ...c,
      card: (result.cards || []).find((card, idx) => idx === i && card.name === c.name) || { name: c.name },
    }));
    // Pair crops to resolved cards by name order of non-unknown crops.
    let ci = 0;
    state.scanCrops.forEach((crop) => {
      if (crop.name && crop.name !== "Unknown" && result.cards && result.cards[ci] && result.cards[ci].name === crop.name) {
        crop.card = result.cards[ci];
        ci += 1;
      }
    });
    syncCardsFromCrops();
    $("#deckName").value = file.name.replace(/\.[^.]+$/, "");
    $("#scanNotes").classList.remove("hidden");
    $("#scanNotes").innerHTML = `<b>${result.source}</b><p>${(result.notes || []).join("<br>")}</p><p class="tiny">${result.detected_regions || 0} card-shaped regions found.</p>`;
    renderEditor();
  } finally {
    document.body.classList.remove("busy");
  }
}

async function loadSample(which) {
  const name = which === "a" ? "set-a.jpg" : "set-b.jpg";
  const blob = await fetch(`/samples/${name}`).then((r) => r.blob());
  const file = new File([blob], which === "a" ? "Carpet Set A.jpg" : "Carpet Set B.jpg", { type: "image/jpeg" });
  await recognizeFile(file);
}

$("#file").addEventListener("change", (e) => {
  if (e.target.files[0]) recognizeFile(e.target.files[0]);
});
$$("[data-sample]").forEach((b) => b.onclick = () => loadSample(b.dataset.sample));

$("#addCard").onclick = async () => {
  const name = $("#addName").value.trim();
  if (!name) return;
  const card = await api("/api/cards/resolve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  state.scanCards.push(card);
  $("#addName").value = "";
  renderEditor();
};

$("#saveDeck").onclick = async () => {
  if (!state.scanCards.length) return alert("Add some cards first.");
  await api("/api/decks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: $("#deckName").value, cards: state.scanCards, source: "scan" }),
  });
  state.decks = await api("/api/decks");
  show("decks");
};

function resultPanel(rec) {
  const r = rec.results || {};
  const a = Math.round((r.win_rate_a || 0) * 100);
  const b = Math.round((r.win_rate_b || 0) * 100);
  const t = Math.round((r.tie_rate || 0) * 100);
  const learn = rec.learning || {};
  return `
    <div class="panel">
      <div class="stat">${a}% / ${b}%</div>
      <p>A wins vs B wins · ${rec.method?.games?.toLocaleString()} games · ${rec.elapsed_seconds}s · seed ${rec.method?.seed}</p>
      <div class="bar"><div class="a" style="width:${a}%"></div><div class="b" style="width:${b}%"></div><div class="t" style="width:${t}%"></div></div>
      <p><b>Method</b><br>${rec.method?.how || ""}</p>
      <p><b>Strategies</b><br>A: ${rec.strategies?.a?.name} — ${rec.strategies?.a?.description}<br>
      B: ${rec.strategies?.b?.name} — ${rec.strategies?.b?.description}</p>
      <p><b>What the AI learned</b><br>${(learn.insights || []).map((i) => "• " + i).join("<br>")}</p>
      ${learn.combo ? `<p class="ok">Pikachu paralyzed Dondozo in ${((learn.combo.p_games_with_success ?? learn.combo.p_landed_per_game) * 100).toFixed(1)}% of games.</p>` : ""}
      <p class="tiny">Lab id ${rec.id}</p>
    </div>`;
}

$("#runSim").onclick = async () => {
  $("#simOut").innerHTML = `<div class="panel">Running ${$("#games").value} games…</div>`;
  document.body.classList.add("busy");
  try {
    const rec = await api("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        deck_a_id: $("#deckA").value,
        deck_b_id: $("#deckB").value,
        strategy_a: $("#stratA").value,
        strategy_b: $("#stratB").value,
        games: +$("#games").value,
        question: $("#simQuestion").value,
      }),
    });
    $("#simOut").innerHTML = resultPanel(rec);
  } catch (err) {
    $("#simOut").innerHTML = `<div class="panel">${err.message}</div>`;
  } finally {
    document.body.classList.remove("busy");
  }
};

$("#runTrades").onclick = async () => {
  $("#simOut").innerHTML = `<div class="panel">Searching win-win trades…</div>`;
  document.body.classList.add("busy");
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
      `<div class="list-item"><div><b>${t.give_a} ⇄ ${t.give_b}</b><div class="tiny">${t.why_a}. ${t.why_b}</div></div><div>${Math.round(t.win_rate_a_after * 100)}% A</div></div>`
    ).join("");
    $("#simOut").innerHTML = `<div class="panel"><p>${rec.method}</p><p>A needs ${ (rec.needs_a||[]).join(", ") || "—" }. B needs ${(rec.needs_b||[]).join(", ") || "—"}.</p>${rows || "No helpful 1-for-1 found."}</div>`;
  } catch (err) {
    $("#simOut").innerHTML = `<div class="panel">${err.message}</div>`;
  } finally {
    document.body.classList.remove("busy");
  }
};

async function sendChat() {
  const message = $("#chatInput").value.trim();
  if (!message) return;
  $("#chatLog").insertAdjacentHTML("beforeend", `<div class="msg user">${md(message)}</div>`);
  $("#chatInput").value = "";
  document.body.classList.add("busy");
  try {
    const res = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, chat_id: state.chatId, history: state.history }),
    });
    state.chatId = res.chat_id;
    state.history = res.messages;
    $("#chatLog").insertAdjacentHTML("beforeend", `<div class="msg bot">${md(res.answer)}</div>`);
    $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
  } catch (err) {
    $("#chatLog").insertAdjacentHTML("beforeend", `<div class="msg bot">${err.message}</div>`);
  } finally {
    document.body.classList.remove("busy");
  }
}
$("#sendChat").onclick = sendChat;

async function renderLab() {
  const rows = await api("/api/simulations");
  $("#labList").innerHTML = rows.map((r) => `
    <div class="panel">
      <div class="list-item">
        <div><b>${r.question || "Match simulation"}</b>
        <div class="tiny">${r.created_at} · ${r.games} games · A win ${(r.win_rate_a * 100).toFixed(1)}%</div>
        <div class="tiny">${(r.learning || []).join(" · ")}</div></div>
        <button class="secondary" data-lab="${r.id}">Open</button>
      </div>
    </div>`).join("") || `<div class="panel">No runs yet.</div>`;
  $$("[data-lab]").forEach((b) => b.onclick = async () => {
    const rec = await api(`/api/simulations/${b.dataset.lab}`);
    $("#labDetail").innerHTML = resultPanel(rec) + `<div class="panel"><b>Sample game</b><p class="tiny">${(rec.sample_games?.[0]?.log || []).join("<br>")}</p></div>`;
  });
}

$$(".nav button").forEach((b) => b.onclick = () => show(b.dataset.view));
boot().catch((err) => { $("#aiPill").textContent = "Error"; console.error(err); });
