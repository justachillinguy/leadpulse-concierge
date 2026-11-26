# AI Search (GEO) & Lead-Capture Website Auditor

Bulk-audit any list of business, SaaS, clinic, or agency websites for **AI search readiness** and **24/7 lead-capture gaps** in seconds.

## What It Extracts Per URL
- `readiness_score` (0–100 composite score)
- `has_llms_txt` & `llms_txt_bytes` (strictly validates real markdown/text, ignoring soft-200 HTML 404 pages)
- `schema_types` (parsed `@type` values from all `application/ld+json` blocks)
- `blocked_ai_bots` (checks `robots.txt` for blocks on `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`)
- `has_live_chat_widget`, `has_whatsapp_link`, `forms_count`
- `public_emails` (filtered for real contact emails, excluding image asset false positives)

## Ideal Use Cases
- SEO & AI Visibility (GEO) agencies auditing client & competitor domains
- Lead-generation teams qualifying SMB websites missing 24/7 conversion widgets
- Automated directory & SaaS market research

## Recommended Apify Store Pricing
- **Pay-Per-Event / Rental:** `$19/month` + usage OR `$0.005` per audited domain (`$5` per 1,000 sites).
