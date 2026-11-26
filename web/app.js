import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import { getFirestore, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";

const fbApp = initializeApp({
  projectId: "leadpulse-concierge-2026",
  appId: "1:346787789629:web:b7dc570a0637b8671ae354",
  apiKey: "AIzaSyCJl9EUM2BRkgNHwDCGiHLIgfuBkXwwMHY",
  authDomain: "leadpulse-concierge-2026.firebaseapp.com",
  storageBucket: "leadpulse-concierge-2026.firebasestorage.app",
  messagingSenderId: "346787789629"
});
const db = getFirestore(fbApp);

const selectEl = document.getElementById("demo-select");
const auditEl = document.getElementById("audit-card");
const mountEl = document.getElementById("widget-mount");
const logEl = document.getElementById("lead-webhook-log");

let demos = [];

function renderDemo(slug) {
  const demo = demos.find((d) => d.slug === slug) || demos[0];
  if (!demo) return;

  const gapsHtml = (demo.audit.gaps || [])
    .map((g) => `<li>${g}</li>`)
    .join("");

  auditEl.innerHTML = `
    <div class="audit-head">
      <div>
        <strong>${demo.name}</strong> · <span style="color:#475569">${demo.category}</span>
      </div>
      <span class="score-badge">Readiness: ${demo.audit.readiness_score}/100</span>
    </div>
    <div style="color:#475569">Site: <a href="${demo.url}" target="_blank" rel="noopener">${demo.url}</a> · Avg Client Value: ~€${demo.avg_ticket_eur}</div>
    ${gapsHtml ? `<ul class="audit-gaps">${gapsHtml}</ul>` : ""}
  `;

  logEl.hidden = true;
  window.LeadPulse.init(
    {
      name: demo.name,
      url: demo.url,
      lang: demo.lang,
      services: demo.services,
      qa: demo.qa,
      onLead: async (lead) => {
        logEl.hidden = false;
        logEl.textContent = `24/7 Cloud Capture -> Saved lead for ${demo.name}: ${lead.service} | ${lead.timeframe} | ${lead.name} (${lead.contact})`;
        try {
          await addDoc(collection(db, "leads"), {
            business: String(demo.name || "Unknown").slice(0, 120),
            demoSlug: String(demo.slug || "default").slice(0, 60),
            service: String(lead.service || "General").slice(0, 120),
            timeframe: String(lead.timeframe || "Flexible").slice(0, 80),
            name: String(lead.name || "").slice(0, 100),
            contact: String(lead.contact || "").slice(0, 160),
            sourceUrl: String(demo.url || "").slice(0, 300),
            createdAt: serverTimestamp()
          });
        } catch (err) {
          console.warn("Firestore lead write:", err);
        }
      },
    },
    mountEl
  );
}

function initROI() {
  const visitors = document.getElementById("r-visitors");
  const ticket = document.getElementById("r-ticket");
  const leads = document.getElementById("r-leads");
  const close = document.getElementById("r-close");

  function update() {
    const v = Number(visitors.value);
    const t = Number(ticket.value);
    const l = Number(leads.value);
    const c = Number(close.value);
    document.getElementById("v-val").textContent = v.toLocaleString("en-US");
    document.getElementById("t-val").textContent = `€${t.toLocaleString("en-US")}`;
    document.getElementById("l-val").textContent = String(l);
    document.getElementById("c-val").textContent = `${c}%`;

    const rev = Math.round(l * (c / 100) * t);
    const mult = (rev / 149).toFixed(1);
    document.getElementById("roi-rev").textContent = `€${rev.toLocaleString("en-US")} / mo`;
    document.getElementById("roi-mult").textContent = `${mult}x return on €149/mo Care Retainer`;
  }

  [visitors, ticket, leads, close].forEach((el) => el.addEventListener("input", update));
  update();
}

async function boot() {
  initROI();
  try {
    const res = await fetch("demos.json");
    const data = await res.json();
    demos = data.demos || [];
  } catch (e) {
    demos = [
      {
        slug: "default",
        name: "Sample Dental Clinic",
        url: "https://example.com",
        category: "Dental Clinic",
        lang: "en",
        avg_ticket_eur: 1200,
        services: ["Dental Implants", "Invisalign", "Teeth Whitening", "Emergency Care"],
        audit: { readiness_score: 45, gaps: ["No 24/7 after-hours intake"] },
        qa: [],
      },
    ];
  }

  selectEl.innerHTML = demos
    .map((d) => `<option value="${d.slug}">${d.name} (${d.lang.toUpperCase()} · ${d.audit.readiness_score}/100)</option>`)
    .join("");

  const params = new URLSearchParams(window.location.search);
  const requested = params.get("demo");
  const initial = demos.some((d) => d.slug === requested) ? requested : demos[0]?.slug;
  if (initial) {
    selectEl.value = initial;
    renderDemo(initial);
  }

  selectEl.addEventListener("change", () => renderDemo(selectEl.value));
}

boot();
