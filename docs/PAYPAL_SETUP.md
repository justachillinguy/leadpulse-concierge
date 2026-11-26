# PayPal Revenue Integration Guide (Verified Account State)

- **Account:** `gabriel.a.s.branco09@gmail.com` (Merchant ID: `Y28SWQPWPNVGQ`)
- **Verified Status (2026-11-26):** Account is currently a **Personal** PayPal account (not Business / "Conta Comercial"), and PayPal is showing a primary-email re-confirmation prompt in Profile Settings.
  - Because it is a Personal account, `paypal.com/ncp/links/create` ("Payment Links and Buttons") and `developer.paypal.com` **Live API credentials** are gated by PayPal on upgrading to **PayPal Business (free)** — Sandbox credentials are active (`Viewing sandbox API credentials`).
  - **PayPal.Me** (`https://www.paypal.com/paypalme/my/landing?entry=marketing`) IS available on Personal accounts once you pick your `@handle`.

## Two Zero-Cost Paths to Live PayPal Checkout

### Path A — Free PayPal.Me Link (Fastest, Works on Current Personal Account)
1. Open `https://www.paypal.com/paypalme/my/landing?entry=marketing` (while signed in).
2. Click **Começar**, choose your PayPal.Me handle (e.g., `gabrielbranco`), and confirm.
3. Paste `https://paypal.me/<your-handle>/29EUR` (and `/390EUR`, `/290EUR`) into `web/pay.html` (`PLANS[...].livePaymentLink`) and set `PAYPAL_CONFIG.mode = "LIVE"`.

### Path B — Free Upgrade to PayPal Business (Unlocks Official Payment Links, Subscriptions & Live Checkout SDK)
1. At `https://www.paypal.com/ncp/links/create`, click **Criar conta Comercial** (free upgrade on PayPal).
2. Create Payment Links / Subscriptions for:
   - **€29.00 EUR** — LeadPulse White-Label Pro Kit
   - **€390.00 EUR** — 48h Pilot Setup
   - **€149.00 EUR / mo** — Care & Optimization Retainer
   - **€290.00 EUR** — Agency White-Label First Site
3. Paste the generated `https://www.paypal.com/ncp/payment/...` URLs into `web/pay.html` and redeploy (`firebase deploy --only hosting`).

## Marketplace Payouts (No Business Upgrade Required)
- **Payhip**, **Gumroad**, and **Apify Store** send payouts straight to `gabriel.a.s.branco09@gmail.com` once connected in each platform's Payout settings.
