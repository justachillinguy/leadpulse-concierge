# BUSINESS PLAN — LeadPulse Concierge (AI Lead-Capture & 24/7 Booking Concierge)

## 1. Selected Opportunity & Positioning
**Brand / Product Name:** **LeadPulse Concierge**  
**Model:** Hybrid **Productized AI Automation Service + Embeddable Micro-SaaS Widget**  
**Core Promise:** *"Turn after-hours website visitors into qualified, pre-booked consultation requests in 48 hours — zero 'Powered By' third-party branding, zero software headaches."*

## 2. Target Customer Segments
### Primary Wedge (Fastest Cashflow)
1. **High-Ticket Local Clinics & Private Practices** (Cosmetic Dentistry, Implantology, Aesthetic Dermatology, Private Clinics in PT/EU & UK/US).
   - Average customer LTV: €800 – €4,500+.
   - Pain: Static contact forms + unstaffed after-hours WhatsApp links lose urgent inquiries at night and weekends.
2. **Web Design & Digital Marketing Agencies (White-Label Multiplier)**
   - Agencies already manage 10–50 SMB websites and look for high-margin AI retainers they can resell without building infrastructure.

## 3. Productized Pricing & Offer Structure (EUR)
| Tier | Price | What's Included | Gross Margin |
|---|---|---|---|
| **Pilot Setup & 48h Launch** | **€390** one-time | Custom concierge trained on client's services/FAQs/locations, bilingual (PT/EN or local), lead qualification flow (treatment, urgency, preferred time, contact), instant email/WhatsApp handoff, 1-line `<script>` install, zero third-party branding, **bonus Schema.org JSON-LD + `llms.txt` AI Search Readiness file** | ~98% |
| **Care & Conversion Retainer** | **€149 / month** | Hosting, monthly FAQ/pricing/offer updates, lead-capture analytics report, priority tweaks | ~95% |
| **Agency White-Label Pack** | **€290/site setup + €99/site/mo** | Resellable under agency brand (compare Chatbase $150/mo + $99/mo white-label add-on) | ~95% |
| **Self-Serve Micro-SaaS (Phase 2)** | **€49 / month** | Self-serve workspace generator for smaller SMBs once core engine & billing are automated | ~95% |

## 4. Technical Architecture (€0 Initial Budget)
1. **Prospect Intelligence & Auto-Demo Generator (`scripts/generate_demo.py`):**
   - Inspects public prospect URL, extracts services, contact details, languages, brand colors, and AI-readiness gaps (JSON-LD, `llms.txt`, after-hours lead capture).
   - Outputs a live interactive JSON config so any prospect gets a custom-branded preview URL (`?demo=<slug>`) with zero manual rework.
2. **Embeddable Concierge Widget (`web/widget.js`) + Landing & Demo Showcase (`web/index.html`):**
   - Pure vanilla JS + CSS shadow-DOM/isolated widget (<25 KB, mobile-responsive, instant load).
   - Smart grounded Q&A engine (retrieval-ranked from verified clinic/business data — zero hallucinated medical claims or fake prices!) + structured multi-step consultation/quote qualifier + booking link / WhatsApp prefilled handoff / `mailto:` / webhook lead dispatch.
   - Optional LLM mode (via client API key or funded API proxy once paid).
   - Hosted for **€0** on **Firebase Hosting (Spark)** or **GitHub Pages**.
3. **PayPal Payment Infrastructure (`gabriel.a.s.branco09@gmail.com`):**
   - Official PayPal Checkout / Payment Links / Invoice workflow prepared in `web/pay.html` and `docs/PAYPAL_SETUP.md`.
   - **Strict safety gate:** Live PayPal credentials/links and external outreach require explicit owner approval before activation.

## 5. Acquisition Engine (Zero Ad Spend)
- **Personalized "Live Demo First" Outreach:** Never send generic cold pitches. Send each verified prospect:
  1. 2 specific observations from their real site (e.g., missing Schema/after-hours intake).
  2. A direct link to a working interactive concierge already tailored to their business.
  3. Clear ROI math + €390 Pilot Guarantee.
- **Channels:** Direct B2B email to verified public business emails, personalized contact-form/LinkedIn replies, HN "Freelancer / Seeking freelancer" monthly thread, and agency partnership pitches.

## 6. Path to €100,000 Cumulative Revenue
| Milestone | Customers / Partners | Pricing Mix | Cumulative Revenue |
|---|---|---|---|
| **Milestone 1 (First Dollar)** | 1 Pilot Client | €390 setup + €149 mo 1 | **€539** |
| **Milestone 2 (Validation)** | 5 Clients | 5 × €390 + €745/mo × 2 mos | **€3,440** |
| **Milestone 3 (Agency Multiplier)** | 15 Direct + 2 Agencies (10 sites) | Setups + €2,735/mo MRR | **~€18,000** |
| **Milestone 4 (Scale + Self-Serve SaaS)** | 45 Managed + 40 Self-Serve (€49–€149/mo) | ~€8,500/mo MRR + setups over 12 mos | **€100,000+** |
