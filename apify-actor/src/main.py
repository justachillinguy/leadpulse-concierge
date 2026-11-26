"""Apify Actor: AI Search (GEO) & Lead-Capture Website Auditor.

Works both inside Apify Cloud (via apify.Actor) and standalone locally
(via JSON stdin/stdout or --urls CLI) for zero-cost testing.
"""

from __future__ import annotations

import asyncio
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AI_BOTS = ("GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended")
BAD_EMAIL_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".css", ".js")


def fetch(url: str, timeout: int = 10) -> tuple[int, str, str]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; LeadPulseAuditor/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        ctype = resp.headers.get("Content-Type", "")
        raw = resp.read(500_000)
        return resp.status, ctype, raw.decode("utf-8", errors="ignore")


def check_llms_txt(origin: str, timeout: int) -> dict:
    try:
        status, ctype, body = fetch(f"{origin}/llms.txt", timeout=min(timeout, 6))
        low = body.lstrip()[:200].lower()
        is_html = "<!doctype html" in low or "<html" in low or "text/html" in ctype.lower()
        valid = status == 200 and not is_html and len(body.strip()) > 30
        return {"present": valid, "http_status": status, "bytes": len(body.strip()) if valid else 0}
    except Exception:
        return {"present": False, "http_status": 0, "bytes": 0}


def check_robots_ai(origin: str, timeout: int) -> dict:
    blocked: list[str] = []
    try:
        status, _, body = fetch(f"{origin}/robots.txt", timeout=min(timeout, 6))
        if status != 200:
            return {"has_robots_txt": False, "blocked_ai_bots": []}
        current_agents: list[str] = []
        for raw_line in body.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, val = [x.strip() for x in line.split(":", 1)]
            if key.lower() == "user-agent":
                current_agents.append(val)
            elif key.lower() == "disallow" and val == "/":
                for bot in AI_BOTS:
                    if any(a.lower() == bot.lower() or a == "*" for a in current_agents) and bot not in blocked:
                        blocked.append(bot)
            elif key.lower() not in ("user-agent", "disallow", "allow"):
                current_agents = []
        return {"has_robots_txt": True, "blocked_ai_bots": blocked}
    except Exception:
        return {"has_robots_txt": False, "blocked_ai_bots": []}


def audit_one(url: str, timeout: int = 10) -> dict:
    parsed = urllib.parse.urlparse(url if "://" in url else f"https://{url}")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    html = ""
    status = 0
    err = ""
    try:
        status, _, html = fetch(parsed.geturl(), timeout=timeout)
    except Exception as exc:
        err = str(exc)

    titles = re.findall(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", titles[0]).strip() if titles else ""
    schemas = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
    schema_types: list[str] = []
    for raw_ld in schemas:
        try:
            obj = json.loads(raw_ld.strip())
            items = obj if isinstance(obj, list) else obj.get("@graph", [obj])
            for it in items:
                if isinstance(it, dict) and it.get("@type"):
                    t = it["@type"]
                    schema_types.extend(t if isinstance(t, list) else [str(t)])
        except Exception:
            pass

    low = html.lower()
    has_chat = any(
        k in low
        for k in ("widget.intercom.io", "code.tidio.co", "client.crisp.chat", "js.driftt.com", "chatbase.co/embed", "embed.tawk.to")
    )
    has_wa = "wa.me/" in low or "api.whatsapp.com" in low
    forms_count = len(re.findall(r"<form\b", low))
    emails = [
        e for e in sorted(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)))
        if not any(e.lower().endswith(ext) for ext in BAD_EMAIL_EXTS)
        and "@2x" not in e.lower()
        and "@4x" not in e.lower()
    ][:5]

    llms_info = check_llms_txt(origin, timeout)
    robots_info = check_robots_ai(origin, timeout)

    score = 20
    if status == 200:
        score += 15
    if schema_types:
        score += 20
    if llms_info["present"]:
        score += 20
    if has_chat:
        score += 20
    elif has_wa:
        score += 10
    if not robots_info["blocked_ai_bots"]:
        score += 5

    return {
        "url": parsed.geturl(),
        "http_status": status,
        "error": err,
        "title": title,
        "readiness_score": score,
        "has_llms_txt": llms_info["present"],
        "llms_txt_bytes": llms_info["bytes"],
        "schema_types": sorted(set(schema_types)),
        "blocked_ai_bots": robots_info["blocked_ai_bots"],
        "has_live_chat_widget": has_chat,
        "has_whatsapp_link": has_wa,
        "forms_count": forms_count,
        "public_emails": emails,
    }


async def main() -> None:
    try:
        from apify import Actor  # type: ignore

        async with Actor:
            inp = await Actor.get_input() or {}
            urls = inp.get("urls") or []
            timeout = int(inp.get("timeoutSeconds") or 10)
            for u in urls:
                res = await asyncio.to_thread(audit_one, u, timeout)
                await Actor.push_data(res)
    except ImportError:
        urls = sys.argv[1:] or ["https://www.dciporto.pt/", "https://www.wheelt.pt/"]
        out = [audit_one(u) for u in urls]
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
