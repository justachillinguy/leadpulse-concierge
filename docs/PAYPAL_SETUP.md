# PayPal Revenue Integration Guide (Official Services)

- **Destination Account:** `gabriel.a.s.branco09@gmail.com`
- **Status:** Pre-Activation (awaiting owner authentication & approval)
- **Fee Benchmark (EEA EUR):** ~2.9%–3.4% + €0.35 per PayPal wallet transaction (~1.2% + €0.35 for eligible guest cards)

## Fastest Activation Path (Zero Backend Cost, 3 Minutes)
1. Owner logs directly into `https://www.paypal.com` (`gabriel.a.s.branco09@gmail.com`) in their own browser.
2. Navigate to **Pay & Get Paid → Payment Links and Buttons** (or `https://www.paypal.com/buttons`).
3. Create 3 official Payment Links / Subscriptions:
   - **Pilot Setup (One-Time):** `€390.00 EUR` — "LeadPulse Concierge — 48h Pilot Setup"
   - **Care Retainer (Subscription):** `€149.00 EUR / month` — "LeadPulse Concierge — Care & Optimization"
   - **Agency White-Label First Site (One-Time):** `€290.00 EUR` — "LeadPulse Agency White-Label Setup"
4. Paste the generated `https://www.paypal.com/ncp/payment/...` URLs into `web/pay.html` (`PLANS[...].livePaymentLink`) and set `PAYPAL_CONFIG.mode = "LIVE"`.

## Optional REST API / Checkout v2 Integration
If dynamic per-client invoicing or automated webhook verification is needed later:
1. Log into `https://developer.paypal.com` with `gabriel.a.s.branco09@gmail.com`.
2. Create a Live App to obtain a `CLIENT_ID` (safe for client-side PayPal JS SDK) and server-side `CLIENT_SECRET` (never stored in client code).
3. Use `POST /v2/checkout/orders` and `POST /v2/checkout/orders/{id}/capture` for automated verification and ledger updates into `REVENUE.md`.

## Security Rules
- Never share passwords or 2FA codes in chat.
- Never transfer, withdraw, or modify payout/banking settings autonomously.
- Live payments remain disabled (`PRE_ACTIVATION`) until explicit owner approval.
