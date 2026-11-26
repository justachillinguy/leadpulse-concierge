"""Prospect Website Auditor & LeadPulse Demo Generator.

Crawls public prospect URLs using stdlib HTTP + HTML parsing (zero paid APIs),
audits AI search readiness & lead-capture gaps, and emits:
1. web/demos.json (live interactive concierge configs for each prospect)
2. deliverables/<slug>/llms.txt and schema.jsonld (ready-to-ship bonus files)
"""

from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
DELIV_DIR = ROOT / "deliverables"

PROSPECTS = [
    {
        "slug": "dciporto",
        "name": "DCI Porto",
        "url": "https://www.dciporto.pt/",
        "category": "Dental & Aesthetic Clinic",
        "lang": "pt",
        "avg_ticket_eur": 1200,
        "booking_note": "Rua 5 de Outubro, 257, Porto",
    },
    {
        "slug": "iron",
        "name": "Clínica IRON",
        "url": "https://iron.pt/",
        "category": "Implantology & Aesthetic Dentistry",
        "lang": "pt",
        "avg_ticket_eur": 1500,
        "booking_note": "Porto (junto à estação da Lapa)",
    },
    {
        "slug": "clinicamacro",
        "name": "Clínica MACRO",
        "url": "https://clinicamacro.pt/",
        "category": "Dental, Aesthetic & Hair Transplant Clinic",
        "lang": "pt",
        "avg_ticket_eur": 2200,
        "booking_note": "Porto e Lisboa",
    },
    {
        "slug": "sdadental",
        "name": "SDA Dental Studio",
        "url": "https://www.sdadentalstudio.co.uk/",
        "category": "Cosmetic & Implant Dentistry",
        "lang": "en",
        "avg_ticket_eur": 1800,
        "booking_note": "Tower Hamlets / Canary Wharf, London",
    },
    {
        "slug": "wheelt",
        "name": "Wheelt Agency",
        "url": "https://www.wheelt.pt/",
        "category": "Web Design & Digital Agency",
        "lang": "pt",
        "avg_ticket_eur": 2500,
        "booking_note": "Portugal (Partner White-Label Demo)",
    },
    {
        "slug": "digiland",
        "name": "Digiland",
        "url": "https://digiland.pt/",
        "category": "Digital Marketing & Web Agency",
        "lang": "pt",
        "avg_ticket_eur": 2000,
        "booking_note": "Portugal (Partner White-Label Demo)",
    },
]

BAD_EMAIL_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".css", ".js")
GENERIC_BAD_EMAILS = ("info@website.com", "example@example.com", "email@example.com")


class SiteParser(HTMLParser):
    """Extracts title, meta description, headings, nav/service labels, and links."""

    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.in_heading = False
        self.in_nav_or_li = False
        self.skip_depth = 0
        self.title_parts: list[str] = []
        self.meta_desc = ""
        self.headings: list[str] = []
        self.list_items: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._buf: list[str] = []
        self._li_buf: list[str] = []
        self._a_href = ""
        self._a_buf: list[str] = []
        self.in_a = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"):
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and (attr_map.get("name") or "").lower() == "description":
            self.meta_desc = (attr_map.get("content") or "").strip()
        elif tag in ("h1", "h2", "h3"):
            self.in_heading = True
            self._buf = []
        elif tag in ("li", "option"):
            self.in_nav_or_li = True
            self._li_buf = []
        elif tag == "a":
            self.in_a = True
            self._a_href = attr_map.get("href") or ""
            self._a_buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript", "svg") and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = False
        elif tag in ("h1", "h2", "h3") and self.in_heading:
            self.in_heading = False
            txt = clean_ws("".join(self._buf))
            if 4 <= len(txt) <= 85:
                self.headings.append(txt)
        elif tag in ("li", "option") and self.in_nav_or_li:
            self.in_nav_or_li = False
            txt = clean_ws("".join(self._li_buf))
            if 4 <= len(txt) <= 55:
                self.list_items.append(txt)
        elif tag == "a" and self.in_a:
            self.in_a = False
            txt = clean_ws("".join(self._a_buf))
            if self._a_href:
                self.links.append((self._a_href, txt))

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
        if self.in_heading:
            self._buf.append(data)
        if self.in_nav_or_li:
            self._li_buf.append(data)
        if self.in_a:
            self._a_buf.append(data)


def clean_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def fetch_url(url: str, timeout: int = 10) -> tuple[int, str, str]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        ctype = resp.headers.get("Content-Type", "")
        raw = resp.read(500_000)
        return resp.status, ctype, raw.decode("utf-8", errors="ignore")


def check_real_llms_txt(base_url: str) -> bool:
    """Verify /llms.txt exists AND is real text/markdown, not a soft-200 HTML page."""
    parsed = urllib.parse.urlparse(base_url)
    root_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"
    try:
        status, ctype, body = fetch_url(root_url, timeout=6)
        if status != 200:
            return False
        low = body.lstrip()[:200].lower()
        if "<!doctype html" in low or "<html" in low or "text/html" in ctype.lower():
            return False
        return len(body.strip()) > 30
    except Exception:
        return False


def extract_emails(html: str) -> list[str]:
    candidates = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
    valid = []
    for email in sorted(set(candidates)):
        low = email.lower()
        if any(low.endswith(ext) for ext in BAD_EMAIL_EXTS):
            continue
        if low in GENERIC_BAD_EMAILS or "@2x" in low or "@3x" in low or "@4x" in low:
            continue
        valid.append(email)
    return valid[:4]


def extract_phones(html: str) -> list[str]:
    tel_matches = re.findall(r'href=["\']tel:([^"\']+)["\']', html, re.I)
    cleaned = []
    for m in tel_matches:
        val = clean_ws(urllib.parse.unquote(m))
        digits = re.sub(r"\D", "", val)
        if 9 <= len(digits) <= 13 and len(set(digits)) > 2:
            cleaned.append(val)
    return list(dict.fromkeys(cleaned))[:3]


def pick_services(headings: list[str], list_items: list[str], category: str, lang: str) -> list[str]:
    noise = {
        "início", "inicio", "home", "sobre", "sobre nós", "about", "about us", "contact",
        "contacto", "contactos", "blog", "login", "search", "menu", "português", "english",
        "política de privacidade", "privacy policy", "termos", "cookies", "skip to content",
        "quem somos", "infraestrutura", "especialidades", "casos clínicos", "a clínica",
        "soluções", "clientes", "projetos recentes.", "projetos recentes", "show reel",
        "kids", "education", "marcações", "equipa", "institucional",
    }
    pool: list[str] = []
    for item in list_items + headings:
        low = item.lower().strip(" .")
        if low in noise or item.lower() in noise or len(item) < 5 or len(item) > 42:
            continue
        if any(bad in low for bad in ("cookie", "rgpd", "gdpr", "copyright", "©", "skip to", "http", "instituto ", "grupo ", "casa ")):
            continue
        if item not in pool:
            pool.append(item)
    if len(pool) >= 4:
        return pool[:5]
    if "Agency" in category:
        return (
            ["Web Design & Landing Pages", "SEO & Local Visibility", "Paid Ads & Funnels", "AI Automation"]
            if lang == "en"
            else ["Criação de Websites", "SEO & Tráfego Pago", "Automação com IA", "Branding & Conversão"]
        )
    return (
        ["Dental Implants", "Invisalign & Orthodontics", "Teeth Whitening & Veneers", "Emergency Consultation"]
        if lang == "en"
        else ["Implantologia Dentária", "Ortodontia Invisível", "Estética & Facetas", "Check-up & Higiene Oral"]
    )


def build_qa_entries(name: str, services: list[str], emails: list[str], phones: list[str], booking_note: str, lang: str) -> list[dict]:
    contact_str = emails[0] if emails else (phones[0] if phones else booking_note)
    svc_list = ", ".join(services[:5])
    if lang == "pt":
        return [
            {
                "keywords": ["serviço", "servicos", "tratamento", "tratamentos", "especialidade", "fazem", "servicos"],
                "q": "Que serviços / tratamentos oferecem?",
                "a": f"Na {name}, disponibilizamos áreas como: {svc_list}. Posso ajudar a pré-qualificar o seu pedido para agendamento em {booking_note}.",
            },
            {
                "keywords": ["preço", "preco", "preços", "valor", "custa", "orçamento", "orcamento", "pagamento"],
                "q": "Qual é o valor ou orçamento?",
                "a": f"O valor exato depende da avaliação inicial do seu caso. Posso recolher os seus dados em 30 segundos para que a equipa da {name} envie uma estimativa ou agende avaliação.",
            },
            {
                "keywords": ["marcar", "marcação", "consulta", "agendar", "reunião", "horario", "horário", "disponibilidade"],
                "q": "Como posso marcar consulta / reunião?",
                "a": f"Pode iniciar a pré-marcação aqui mesmo em 3 passos (24/7), indicando o serviço pretendido e o melhor horário, ou contactar diretamente ({contact_str}).",
            },
            {
                "keywords": ["onde", "morada", "localização", "localizacao", "contacto", "telefone", "email"],
                "q": "Onde ficam localizados e contactos?",
                "a": f"{name} atende em {booking_note}. Contacto público: {contact_str}.",
            },
        ]
    return [
        {
            "keywords": ["service", "services", "treatment", "treatments", "offer", "do you do"],
            "q": "What services / treatments do you offer?",
            "a": f"At {name}, core offerings include: {svc_list}. Tell me what you are looking for and I can pre-qualify your inquiry in 30 seconds.",
        },
        {
            "keywords": ["price", "pricing", "cost", "how much", "quote", "finance", "fee"],
            "q": "How much does it cost / payment options?",
            "a": f"Exact pricing depends on your initial assessment and scope. Leave your goals and contact details here and {name} will reply with tailored options.",
        },
        {
            "keywords": ["book", "appointment", "consultation", "schedule", "call", "availability"],
            "q": "How can I book a consultation?",
            "a": f"You can submit a priority consultation request right here in 3 quick steps (24/7), or reach us via {contact_str}.",
        },
        {
            "keywords": ["where", "location", "address", "contact", "phone", "email"],
            "q": "Where are you located?",
            "a": f"{name} serves clients at {booking_note}. Direct contact: {contact_str}.",
        },
    ]


def build_deliverables(prospect: dict, title: str, desc: str, services: list[str], emails: list[str], phones: list[str]) -> None:
    out_dir = DELIV_DIR / prospect["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    llms_txt = (
        f"# {prospect['name']}\n\n"
        f"> {desc or title or prospect['category']}\n\n"
        f"## Core Services\n"
        + "\n".join(f"- {s}" for s in services)
        + f"\n\n## Location & Contact\n"
        f"- Location: {prospect['booking_note']}\n"
        f"- Website: {prospect['url']}\n"
        + (f"- Email: {emails[0]}\n" if emails else "")
        + (f"- Phone: {phones[0]}\n" if phones else "")
    )
    (out_dir / "llms.txt").write_text(llms_txt, encoding="utf-8")

    schema = {
        "@context": "https://schema.org",
        "@type": "MedicalClinic" if "Dental" in prospect["category"] or "Clinic" in prospect["category"] else "ProfessionalService",
        "name": prospect["name"],
        "url": prospect["url"],
        "description": desc or title,
        "areaServed": prospect["booking_note"],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}} for s in services],
    }
    if emails:
        schema["email"] = emails[0]
    if phones:
        schema["telephone"] = phones[0]
    (out_dir / "schema.jsonld").write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")


def audit_prospect(prospect: dict) -> dict:
    url = prospect["url"]
    html = ""
    status = 0
    try:
        status, _, html = fetch_url(url, timeout=10)
    except Exception as exc:
        print(f"[WARN] Could not fetch {url}: {exc}")

    parser = SiteParser()
    if html:
        parser.feed(html)

    title = clean_ws("".join(parser.title_parts)) or prospect["name"]
    desc = parser.meta_desc
    emails = extract_emails(html)
    phones = extract_phones(html)
    has_ld = "application/ld+json" in html.lower()
    has_llms = check_real_llms_txt(url)
    has_wa = "wa.me/" in html.lower() or "api.whatsapp.com" in html.lower()
    has_ai_chat = any(
        k in html.lower()
        for k in ("widget.intercom.io", "code.tidio.co", "client.crisp.chat", "js.driftt.com", "chatbase.co/embed", "embed.tawk.to")
    )
    services = pick_services(parser.headings, parser.list_items, prospect["category"], prospect["lang"])

    score = 35
    if has_ld:
        score += 20
    if has_llms:
        score += 20
    if has_ai_chat:
        score += 25
    elif has_wa:
        score += 10

    gaps = []
    if not has_ai_chat:
        gaps.append(
            "Sem qualificação automática 24/7 (visitantes fora de horas ficam sem resposta imediata)"
            if prospect["lang"] == "pt"
            else "No 24/7 automated lead qualifier (after-hours visitors leave uncaptured)"
        )
    if not has_ld:
        gaps.append(
            "Sem dados estruturados Schema.org (JSON-LD) para Google e motores de IA"
            if prospect["lang"] == "pt"
            else "Missing Schema.org JSON-LD structured data for Google & AI engines"
        )
    if not has_llms:
        gaps.append(
            "Sem ficheiro /llms.txt válido para visibilidade em ChatGPT/Perplexity"
            if prospect["lang"] == "pt"
            else "Missing valid /llms.txt for ChatGPT & Perplexity visibility"
        )

    build_deliverables(prospect, title, desc, services, emails, phones)

    return {
        "slug": prospect["slug"],
        "name": prospect["name"],
        "url": url,
        "http_status": status,
        "category": prospect["category"],
        "lang": prospect["lang"],
        "avg_ticket_eur": prospect["avg_ticket_eur"],
        "booking_note": prospect["booking_note"],
        "public_email": emails[0] if emails else "",
        "public_phone": phones[0] if phones else "",
        "services": services,
        "audit": {
            "readiness_score": score,
            "has_schema_ld": has_ld,
            "has_real_llms_txt": has_llms,
            "has_whatsapp_link": has_wa,
            "has_ai_concierge": has_ai_chat,
            "gaps": gaps,
        },
        "qa": build_qa_entries(
            prospect["name"], services, emails, phones, prospect["booking_note"], prospect["lang"]
        ),
    }


def main() -> None:
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for p in PROSPECTS:
        print(f"Auditing {p['name']} ({p['url']})...")
        item = audit_prospect(p)
        results.append(item)
        print(
            f"  -> status={item['http_status']} score={item['audit']['readiness_score']}/100 "
            f"ld={item['audit']['has_schema_ld']} llms={item['audit']['has_real_llms_txt']} "
            f"email={item['public_email'] or '-'}"
        )

    out_path = WEB_DIR / "demos.json"
    out_path.write_text(json.dumps({"demos": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {len(results)} live demos to {out_path}")


if __name__ == "__main__":
    main()
