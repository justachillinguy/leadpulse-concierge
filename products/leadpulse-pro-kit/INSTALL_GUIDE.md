# LeadPulse White-Label Pro Kit — 2-Minute Setup Guide

## 1. Generate Client Files in 10 Seconds
- Open `web/generator.html` locally in any browser (or run `python scripts/generate_demo.py` for bulk URL auditing).
- Fill in your business/client details to export `llms.txt`, `schema.jsonld`, and your widget JSON config.

## 2. Remove Branding (White-Label Mode)
- Ensure `poweredBy` is omitted or set to `false` in `LeadPulse.init(config, target)`.
- Host `widget.js` on your own domain, Firebase Hosting, or GitHub Pages.

## 3. Embed on Any Website
- **WordPress / Elementor / Wix / Webflow / Shopify:** Paste the `<div id="leadpulse-mount"></div>` + `<script src="widget.js">` snippet into your footer or custom HTML block.
- **AI Search Visibility:** Upload `llms.txt` to your site root (`https://yourdomain.com/llms.txt`) and paste `schema.jsonld` inside `<head>`.
