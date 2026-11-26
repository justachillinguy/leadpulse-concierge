/**
 * LeadPulse Concierge — Embeddable 24/7 Lead Qualification Widget
 * Zero external runtime dependencies, Shadow DOM isolated, <20KB.
 */
(function () {
  "use strict";

  const I18N = {
    pt: {
      online: "Concierge Online 24/7",
      subtitle: "Resposta imediata & pré-marcação",
      placeholder: "Escreva a sua dúvida ou escolha uma opção...",
      send: "Enviar",
      qualifyCta: "Pedir Marcação / Orçamento",
      stepService: "Qual o serviço ou tratamento pretendido?",
      stepTime: "Quando prefere ser contactado(a) / atendido(a)?",
      times: ["Hoje / Urgente", "Esta semana", "Próximas 2 semanas", "Apenas a informar-me"],
      stepContact: "Indique o seu Nome e Telemóvel ou Email para confirmação:",
      namePh: "O seu nome",
      contactPh: "Telemóvel ou Email",
      submitLead: "Confirmar Pedido Prioritário",
      leadDone: "Pedido registado! A nossa equipa recebeu os seus dados e entrará em contacto rapidamente.",
      fallback: "Posso ajudar com informações sobre serviços, valores indicativos ou marcação prioritária. Clique abaixo para avançar em 30 segundos:",
      greeting: (name) => `Olá! Bem-vindo(a) à ${name}. Como posso ajudar hoje?`,
    },
    en: {
      online: "24/7 AI Concierge",
      subtitle: "Instant answers & priority booking",
      placeholder: "Ask a question or pick a quick option...",
      send: "Send",
      qualifyCta: "Book Consultation / Quote",
      stepService: "Which service or treatment are you interested in?",
      stepTime: "What is your preferred timeframe?",
      times: ["Today / Urgent", "This week", "Next 2 weeks", "Just researching"],
      stepContact: "Enter your Name and Phone or Email for confirmation:",
      namePh: "Your full name",
      contactPh: "Phone or Email",
      submitLead: "Confirm Priority Request",
      leadDone: "Request captured! Our team has received your details and will follow up shortly.",
      fallback: "I can answer questions about services, indicative pricing, or schedule your consultation in 30 seconds:",
      greeting: (name) => `Hi! Welcome to ${name}. How can I help you today?`,
    },
  };

  function scoreMatch(query, qaItem) {
    const q = query.toLowerCase();
    let score = 0;
    for (const kw of qaItem.keywords || []) {
      if (q.includes(kw.toLowerCase())) score += 3;
    }
    for (const word of q.split(/\s+/)) {
      if (word.length > 3 && qaItem.a.toLowerCase().includes(word)) score += 1;
    }
    return score;
  }

  function createWidget(config, mountTarget) {
    const lang = config.lang === "pt" ? "pt" : "en";
    const t = I18N[lang];
    const accent = config.accent || "#0f766e";

    let host = mountTarget;
    if (!host) {
      host = document.createElement("div");
      host.id = "leadpulse-widget-root";
      document.body.appendChild(host);
    }
    if (host.shadowRoot) host.shadowRoot.innerHTML = "";
    const shadow = host.shadowRoot || host.attachShadow({ mode: "open" });

    shadow.innerHTML = `
      <style>
        :host { all: initial; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .lp-shell {
          width: 100%; max-width: 400px; background: #ffffff; border: 1px solid #e2e8f0;
          border-radius: 16px; box-shadow: 0 20px 45px rgba(15, 23, 42, 0.14);
          overflow: hidden; display: flex; flex-direction: column; color: #0f172a;
        }
        .lp-head {
          background: ${accent}; color: #fff; padding: 14px 16px;
          display: flex; align-items: center; justify-content: space-between;
        }
        .lp-title { font-weight: 700; font-size: 15px; margin: 0; }
        .lp-sub { font-size: 12px; opacity: 0.9; display: flex; align-items: center; gap: 6px; margin-top: 2px; }
        .lp-dot { width: 8px; height: 8px; border-radius: 50%; background: #4ade80; display: inline-block; }
        .lp-msgs {
          height: 310px; overflow-y: auto; padding: 14px; background: #f8fafc;
          display: flex; flex-direction: column; gap: 10px;
        }
        .lp-msg {
          max-width: 86%; padding: 10px 12px; border-radius: 12px; font-size: 13.5px; line-height: 1.45;
        }
        .lp-bot { background: #ffffff; border: 1px solid #e2e8f0; align-self: flex-start; border-bottom-left-radius: 4px; }
        .lp-user { background: ${accent}; color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
        .lp-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .lp-chip {
          background: #fff; border: 1px solid #cbd5e1; color: #0f172a; border-radius: 999px;
          padding: 6px 11px; font-size: 12px; cursor: pointer; font-weight: 500;
        }
        .lp-chip:hover { border-color: ${accent}; color: ${accent}; background: #f0fdfa; }
        .lp-chip-primary { background: ${accent}; color: #fff; border-color: ${accent}; }
        .lp-chip-primary:hover { opacity: 0.92; color: #fff; background: ${accent}; }
        .lp-form { display: flex; flex-direction: column; gap: 7px; margin-top: 8px; }
        .lp-input {
          padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 13px; width: 100%; box-sizing: border-box;
        }
        .lp-bar {
          display: flex; gap: 8px; padding: 10px 12px; border-top: 1px solid #e2e8f0; background: #fff;
        }
        .lp-bar input {
          flex: 1; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 10px; font-size: 13px; outline: none;
        }
        .lp-bar button {
          background: ${accent}; color: #fff; border: none; border-radius: 8px; padding: 8px 14px;
          font-weight: 600; font-size: 13px; cursor: pointer;
        }
        .lp-lead-box {
          background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; padding: 10px;
          border-radius: 10px; font-size: 12.5px; margin-top: 6px;
        }
      </style>
      <div class="lp-shell" role="region" aria-label="${config.name} Concierge">
        <div class="lp-head">
          <div>
            <div class="lp-title">${config.name}</div>
            <div class="lp-sub"><span class="lp-dot"></span> ${t.online} · ${t.subtitle}</div>
          </div>
        </div>
        <div class="lp-msgs" id="lp-msgs"></div>
        <form class="lp-bar" id="lp-chat-form">
          <input id="lp-text" type="text" placeholder="${t.placeholder}" autocomplete="off" />
          <button type="submit">${t.send}</button>
        </form>
      </div>
    `;

    const msgsEl = shadow.getElementById("lp-msgs");
    const formEl = shadow.getElementById("lp-chat-form");
    const inputEl = shadow.getElementById("lp-text");
    const state = { service: "", timeframe: "", name: "", contact: "" };

    function scrollBottom() {
      msgsEl.scrollTop = msgsEl.scrollHeight;
    }

    function addBot(text, extraEl) {
      const div = document.createElement("div");
      div.className = "lp-msg lp-bot";
      div.textContent = text;
      if (extraEl) div.appendChild(extraEl);
      msgsEl.appendChild(div);
      scrollBottom();
    }

    function addUser(text) {
      const div = document.createElement("div");
      div.className = "lp-msg lp-user";
      div.textContent = text;
      msgsEl.appendChild(div);
      scrollBottom();
    }

    function startQualification() {
      const wrap = document.createElement("div");
      wrap.className = "lp-chips";
      (config.services || []).slice(0, 5).forEach((svc) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "lp-chip";
        b.textContent = svc;
        b.onclick = () => {
          state.service = svc;
          addUser(svc);
          askTimeframe();
        };
        wrap.appendChild(b);
      });
      addBot(t.stepService, wrap);
    }

    function askTimeframe() {
      const wrap = document.createElement("div");
      wrap.className = "lp-chips";
      t.times.forEach((tm) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "lp-chip";
        b.textContent = tm;
        b.onclick = () => {
          state.timeframe = tm;
          addUser(tm);
          askContact();
        };
        wrap.appendChild(b);
      });
      addBot(t.stepTime, wrap);
    }

    function askContact() {
      const f = document.createElement("form");
      f.className = "lp-form";
      f.innerHTML = `
        <input class="lp-input" required name="name" placeholder="${t.namePh}" />
        <input class="lp-input" required name="contact" placeholder="${t.contactPh}" />
        <button type="submit" class="lp-chip lp-chip-primary">${t.submitLead}</button>
      `;
      f.onsubmit = (e) => {
        e.preventDefault();
        state.name = f.elements.name.value.trim();
        state.contact = f.elements.contact.value.trim();
        if (!state.name || !state.contact) return;
        addUser(`${state.name} (${state.contact})`);
        const box = document.createElement("div");
        box.className = "lp-lead-box";
        box.innerHTML = `<strong>${config.name} Lead Summary:</strong><br/>• ${state.service}<br/>• ${state.timeframe}<br/>• ${state.name} — ${state.contact}`;
        addBot(t.leadDone, box);
        if (typeof config.onLead === "function") {
          config.onLead({ ...state, business: config.name, url: config.url });
        }
      };
      addBot(t.stepContact, f);
    }

    function addStarterChips() {
      const wrap = document.createElement("div");
      wrap.className = "lp-chips";
      const cta = document.createElement("button");
      cta.type = "button";
      cta.className = "lp-chip lp-chip-primary";
      cta.textContent = t.qualifyCta;
      cta.onclick = () => {
        addUser(t.qualifyCta);
        startQualification();
      };
      wrap.appendChild(cta);

      (config.qa || []).slice(0, 3).forEach((item) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "lp-chip";
        b.textContent = item.q;
        b.onclick = () => handleQuery(item.q);
        wrap.appendChild(b);
      });
      addBot(t.greeting(config.name), wrap);
    }

    function handleQuery(text) {
      const q = text.trim();
      if (!q) return;
      addUser(q);
      let best = null;
      let bestScore = 0;
      for (const item of config.qa || []) {
        const s = scoreMatch(q, item);
        if (s > bestScore) {
          bestScore = s;
          best = item;
        }
      }
      const wrap = document.createElement("div");
      wrap.className = "lp-chips";
      const cta = document.createElement("button");
      cta.type = "button";
      cta.className = "lp-chip lp-chip-primary";
      cta.textContent = t.qualifyCta;
      cta.onclick = () => {
        addUser(t.qualifyCta);
        startQualification();
      };
      wrap.appendChild(cta);
      addBot(best ? best.a : t.fallback, wrap);
    }

    formEl.onsubmit = (e) => {
      e.preventDefault();
      const val = inputEl.value;
      inputEl.value = "";
      handleQuery(val);
    };

    addStarterChips();
  }

  window.LeadPulse = { init: createWidget };
})();
