# NexFlo Cloud website

Static site for nexflo.cloud. There's no framework and nothing to install.

```
assets/      styles.css, main.js, logo.png, cloud-icon.png, favicons, hero-cloud.jpg,
             cloud-glow.jpg, og-image.jpg, launch-graphic.jpg
build.py     every page's copy plus the shared header and footer
dist/        built site (upload this folder to your host)
```

## Edit and build

Change copy in `build.py`, then run:

```bash
python3 build.py
```

To preview, open `dist/index.html` in a browser. Any static host works with `dist/`: Netlify, Cloudflare Pages, Azure Static Web Apps or GitHub Pages.

## Deploy on Vercel

The repo is ready for Vercel. `vercel.json` tells it to run `python3 build.py` and serve `dist/`, with clean URLs (`/pricing` instead of `/pricing.html`), security headers and asset caching. No framework or `package.json` is needed.

**Option A: GitHub (recommended, redeploys on every push)**
1. Create an empty GitHub repo (e.g. `nexflo-site`) and push this folder to it.
2. In Vercel: **Add New → Project → Import** that repo. Leave the framework preset as **Other**; the settings come from `vercel.json`. Click **Deploy**.

**Option B: from your computer, no GitHub**
```bash
npx vercel
```
Then run `npx vercel --prod` to publish to production.

**Domains** (Vercel project → Settings → Domains)
- Add `nexflo.cloud` and `www.nexflo.cloud`, then set the DNS records Vercel shows at your domain registrar.
- Add `app.nexflo.cloud` to the same project. `vercel.json` already serves the "portal coming soon" page there. When the real portal exists, remove that domain and the rewrite, and set `PORTAL_URL` in `build.py`.

## Dark and light mode

The site follows the visitor's browser or device setting (dark or light), and switches live if that setting changes. The sun/moon button in the header overrides it, and that choice is remembered. With no setting, it opens in dark mode. Dark styles live in `assets/theme-dark.css`.

## Before launch

- **Brand assets are in place.** `logo.png` is your wordmark with a transparent background. The hero art is the cloud and ribbon from the launch graphic, with the text removed. The favicons and the dark sign-up band's glow come from your cloud icons. `og-image.jpg` (1200×630) is the social sharing image. If you have a vector (SVG) logo, use it instead of `logo.png` for sharper edges.
- **Forms.** Set `FORM_ENDPOINT` at the top of `assets/main.js`. A Power Automate "When an HTTP request is received" flow that emails your Microsoft 365 inbox works well; Formspree is another option. Each submission arrives as JSON with `form`, `to` (aadithbalaji@ for early access, pricing and demos; support@ for the contact form), `page` and `fields`. Until the endpoint is set, forms open a pre-filled email instead.
- **Analytics.** Paste your snippet where the `<!-- Analytics -->` comment sits in `layout()` in `build.py`.
- **Portal.** Deploy `dist/portal.html` as app.nexflo.cloud, then set `PORTAL_URL = "https://app.nexflo.cloud"` in `build.py`.
- **Copy to fill in.** Confirm `LINKEDIN` and the TechDigital details on the About page ("since 2008", and add a link to its website if you want one).
- **Legal.** `privacy.html` and `terms.html` are drafts and need a lawyer's review.
- **Product name.** If TradeFlo becomes OrderFlo, rename it in the `PRODUCTS` list and run find-and-replace in `build.py`.
