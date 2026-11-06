#!/usr/bin/env python3
"""
NexFlo Cloud static site builder.

Every page shares one header and footer, defined here. Edit copy in this file,
then run:  python3 build.py   →  writes the finished HTML into ./dist

No dependencies beyond Python 3.8+.
"""
import html
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"

# ---------------------------------------------------------------- settings
SITE_URL = "https://nexflo.cloud"
SALES = "sales@nexflo.cloud"
INFO = "info@nexflo.cloud"
# Until app.nexflo.cloud exists, "Portal login" points at the local placeholder.
# Deploy dist/portal.html as the index of app.nexflo.cloud, then set this to "https://app.nexflo.cloud".
PORTAL_URL = "portal.html"
LINKEDIN = "https://www.linkedin.com/company/nexflo-cloud"  # TODO: confirm company page URL
YEAR = "2026"

# ---------------------------------------------------------------- icons
ICONS = {
    "plug": '<path d="M9 2v6M15 2v6M6 8h12v3a6 6 0 0 1-12 0V8zM12 17v5"/>',
    "swap": '<path d="M4 7h13l-3-3M20 17H7l3 3"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "tag": '<path d="M3 12V3h9l9 9-9 9-9-9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "rocket": '<path d="M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2M9 15l-3-3c1-4 5-9 13-9 0 8-5 12-9 13l-1-1z"/><circle cx="15" cy="9" r="1.5"/>',
    "code": '<path d="M8 6l-6 6 6 6M16 6l6 6-6 6"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "factory": '<path d="M2 20V9l6 4V9l6 4V4h6v16H2zM6 16h2M11 16h2M16 16h2"/>',
    "truck": '<path d="M1 5h13v11H1zM14 9h4l4 4v3h-8z"/><circle cx="5.5" cy="18" r="2"/><circle cx="17.5" cy="18" r="2"/>',
    "clipboard": '<path d="M9 3h6v3H9zM6 5H4v16h16V5h-2M8 12h8M8 16h5"/>',
    "pulse": '<path d="M2 12h4l3-8 4 16 3-8h6"/>',
    "lock": '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3"/>',
    "eye": '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/>',
    "doc": '<path d="M6 2h9l5 5v15H6zM14 2v6h6M9 13h8M9 17h6"/>',
    "bell": '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10 21h4"/>',
    "users": '<circle cx="9" cy="8" r="4"/><path d="M1 21a8 8 0 0 1 16 0M17 4a4 4 0 0 1 0 8M23 21a8 8 0 0 0-5-7.4"/>',
    "server": '<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6.5h.01M7 17.5h.01"/>',
    "route": '<circle cx="6" cy="19" r="3"/><circle cx="18" cy="5" r="3"/><path d="M9 19h6.5a3.5 3.5 0 0 0 0-7h-7a3.5 3.5 0 0 1 0-7H15"/>',
    "shield": '<path d="M12 2l8 3v6c0 5-3.5 9.5-8 11-4.5-1.5-8-6-8-11V5z"/>',
    "map": '<path d="M9 3L3 6v15l6-3 6 3 6-3V3l-6 3zM9 3v15M15 6v15"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
}


def icon(name, cls="icon"):
    return (f'<span class="{cls}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg></span>')


CHEV = '<svg class="chev" viewBox="0 0 10 10" aria-hidden="true"><path d="M2 3.5l3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
LINKEDIN_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.4 2H3.6A1.6 1.6 0 0 0 2 3.6v16.8A1.6 1.6 0 0 0 3.6 22h16.8a1.6 1.6 0 0 0 1.6-1.6V3.6A1.6 1.6 0 0 0 20.4 2zM8 19H5V9h3zM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4zM19 19h-3v-4.9c0-1.2 0-2.7-1.6-2.7S12.5 12.7 12.5 14v5h-3V9h2.9v1.4c.4-.8 1.4-1.6 2.9-1.6 3.1 0 3.7 2 3.7 4.7z"/></svg>'

# ---------------------------------------------------------------- products & solutions data
PRODUCTS = [
    dict(key="tradeflo", name="TradeFlo", mark="Trade", href="tradeflo.html", status="live",
         line="EDI for manufacturers, distributors and retail suppliers: orders, invoices and ship notices with your trading partners."),
    dict(key="careflo", name="CareFlo", mark="Care", href="careflo.html", status="soon",
         line="Healthcare claims and eligibility translation, built for medical billing and RCM teams."),
    dict(key="healthflo", name="HealthFlo", mark="Health", href="healthflo.html", status="soon",
         line="HL7 v2 and FHIR data exchange, built for health tech and hospital systems."),
]

SOLUTIONS = [
    dict(key="manufacturers", name="Manufacturers and suppliers", href="manufacturers.html", icon="factory", product="TradeFlo",
         short="Meet retailer EDI requirements without the legacy price tag."),
    dict(key="logistics", name="Logistics and distribution", href="logistics.html", icon="truck", product="TradeFlo",
         short="Many trading partners, one place to manage every document."),
    dict(key="medical-billing", name="Medical billing and RCM", href="medical-billing.html", icon="clipboard", product="CareFlo",
         short="Claims and eligibility transactions across payers, in one format."),
    dict(key="health-tech", name="Health tech and EHR teams", href="health-tech.html", icon="pulse", product="HealthFlo",
         short="Connect systems that format clinical data differently."),
]


def status_badge(status):
    return ('<span class="badge badge-live">Early access</span>' if status == "live"
            else '<span class="badge badge-soon">Coming 2027</span>')


# ---------------------------------------------------------------- code highlighting
def hl_edi(text):
    """Highlight X12 / HL7: segment IDs in blue."""
    out = []
    for line in text.strip("\n").split("\n"):
        esc = html.escape(line)
        m = re.match(r"^([A-Z0-9]{2,3})([*|])", esc)
        if m:
            esc = f'<span class="seg">{m.group(1)}</span>' + esc[len(m.group(1)):]
        out.append(esc)
    return "\n".join(out)


def hl_json(text):
    esc = html.escape(text.strip("\n"), quote=False)
    esc = re.sub(r'"([^"]+)"(\s*:)', r'<span class="k">"\1"</span>\2', esc)
    esc = re.sub(r'(:\s*|\[\s*|,\s*)"([^"]*)"', r'\1<span class="s">"\2"</span>', esc)
    esc = re.sub(r'(:\s*)(-?\d+(?:\.\d+)?)', r'\1<span class="n">\2</span>', esc)
    return esc


def code_block(title, tag, body):
    return f'<div class="code"><div class="code-head"><b>{title}</b><span>{tag}</span></div><pre><code>{body}</code></pre></div>'


def translate_demo(left_title, left_tag, left_raw, right_title, right_tag, right_raw, mid="Translate", left_kind="edi"):
    left = hl_edi(left_raw) if left_kind == "edi" else hl_json(left_raw)
    return f'''<div class="translate">
  {code_block(left_title, left_tag, left)}
  <div class="translate-mid"><div class="pill"><i>→</i>{mid}</div></div>
  {code_block(right_title, right_tag, hl_json(right_raw))}
</div>'''


PO_X12 = """
ST*850*0001~
BEG*00*SA*4500018273**20261104~
REF*IA*554433~
DTM*010*20261118~
N1*ST*WALMART DC 6094*UL*0078742000008~
PO1*1*240*EA*4.85**UP*012345678905*IN*009876543~
PID*F****STAINLESS WATER BOTTLE 24OZ~
CTT*1~
SE*10*0001~
"""

PO_JSON = """
{
  "type": "purchase_order",
  "standard": "X12 850",
  "partner": "Walmart",
  "po_number": "4500018273",
  "po_date": "2026-11-04",
  "ship_by": "2026-11-18",
  "ship_to": {
    "name": "Walmart DC 6094",
    "gln": "0078742000008"
  },
  "lines": [{
    "upc": "012345678905",
    "description": "Stainless Water Bottle 24oz",
    "qty": 240,
    "unit_price": 4.85
  }]
}
"""

CLAIM_X12 = """
ST*837*0001*005010X222A1~
BHT*0019*00*CLM20261104*20261104*1030*CH~
NM1*85*2*LAKESIDE FAMILY CLINIC*****XX*1234567893~
NM1*IL*1*DOE*JANE****MI*W123456789~
CLM*PT1001*185***11:B:1*Y*A*Y*Y~
HI*ABK:J069~
SV1*HC:99213*185*UN*1***1~
DTP*472*D8*20261103~
SE*9*0001~
"""

CLAIM_JSON = """
{
  "type": "professional_claim",
  "standard": "X12 837P",
  "claim_id": "PT1001",
  "billing_provider": {
    "name": "Lakeside Family Clinic",
    "npi": "1234567893"
  },
  "patient": { "member_id": "W123456789" },
  "diagnosis": ["J06.9"],
  "services": [{
    "cpt": "99213",
    "date": "2026-11-03",
    "charge": 185
  }],
  "total_charge": 185
}
"""

HL7_MSG = """
MSH|^~\\&|ADT|MERCY_HOSP|NEXFLO|HEALTHFLO|20261104103000||ADT^A01|MSG00001|P|2.5.1
EVN|A01|20261104103000
PID|1||MRN448812^^^MERCY^MR||DOE^JANE^A||19840212|F|||12 LAKE ST^^DULUTH^MN^55802
PV1|1|I|4W^412^1^MERCY||||1234567893^SMITH^ALAN
"""

FHIR_JSON = """
{
  "resourceType": "Patient",
  "identifier": [{
    "system": "urn:mercy:mrn",
    "value": "MRN448812"
  }],
  "name": [{ "family": "Doe", "given": ["Jane", "A"] }],
  "gender": "female",
  "birthDate": "1984-02-12",
  "address": [{
    "city": "Duluth",
    "state": "MN",
    "postalCode": "55802"
  }]
}
"""


# ---------------------------------------------------------------- shared components
def nav_html(active):
    def act(key):
        return ' active' if active == key else ''

    products_dd = "".join(
        f'<a href="{p["href"]}"><span class="d-icon">{p["name"][0]}F</span><span><span class="d-title">{p["name"]} '
        f'{status_badge(p["status"])}</span><span class="d-desc">{p["line"]}</span></span></a>' for p in PRODUCTS)
    solutions_dd = "".join(
        f'<a href="{s["href"]}">{icon(s["icon"], "d-icon")}<span><span class="d-title">{s["name"]}</span>'
        f'<span class="d-desc">{s["short"]}</span></span></a>' for s in SOLUTIONS)
    return f'''<header class="site-header">
  <a class="skip" href="#main">Skip to content</a>
  <nav class="container nav" aria-label="Main">
    <a class="brand" href="index.html" aria-label="NexFlo Cloud home"><img src="assets/logo.png" alt="NexFlo Cloud" width="154" height="46"></a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <div class="nav-panel">
      <ul class="nav-menu">
        <li class="nav-item has-dd"><button class="nav-link{act("products")}" aria-expanded="false">Products {CHEV}</button>
          <div class="dropdown">{products_dd}<div class="d-foot"><a href="products.html">All products →</a></div></div></li>
        <li class="nav-item has-dd"><button class="nav-link{act("solutions")}" aria-expanded="false">Solutions {CHEV}</button>
          <div class="dropdown">{solutions_dd}<div class="d-foot"><a href="solutions.html">Solutions overview →</a></div></div></li>
        <li class="nav-item"><a class="nav-link{act("pricing")}" href="pricing.html">Pricing</a></li>
        <li class="nav-item has-dd"><button class="nav-link{act("resources")}" aria-expanded="false">Resources {CHEV}</button>
          <div class="dropdown">
            <a href="resources.html">{icon("doc", "d-icon")}<span><span class="d-title">Blog and EDI guides</span><span class="d-desc">Plain-language explainers on EDI and healthcare transactions.</span></span></a>
            <a href="security.html">{icon("shield", "d-icon")}<span><span class="d-title">Security</span><span class="d-desc">How we plan to protect your data.</span></span></a>
            <a href="resources.html#faq">{icon("chat", "d-icon")}<span><span class="d-title">FAQ</span><span class="d-desc">Answers to common questions.</span></span></a>
          </div></li>
        <li class="nav-item has-dd"><button class="nav-link{act("company")}" aria-expanded="false">Company {CHEV}</button>
          <div class="dropdown" style="min-width:260px">
            <a href="about.html">{icon("users", "d-icon")}<span><span class="d-title">About</span><span class="d-desc">Who we are and why we're building NexFlo.</span></span></a>
            <a href="contact.html">{icon("chat", "d-icon")}<span><span class="d-title">Contact</span><span class="d-desc">Talk to the team directly.</span></span></a>
          </div></li>
      </ul>
      <div class="nav-actions">
        <a class="nav-login" href="{PORTAL_URL}">Portal login</a>
        <a class="btn btn-secondary btn-sm" href="demo.html">Book a demo</a>
        <a class="btn btn-primary btn-sm" href="early-access.html">Get early access</a>
      </div>
    </div>
  </nav>
</header>'''


def footer_html():
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/logo.png" alt="NexFlo Cloud" width="154" height="46">
        <p>Less friction. More flow. Simpler EDI for growing businesses.</p>
        <p class="mt-2"><a href="mailto:{SALES}">{SALES}</a></p>
        <a class="social" href="{LINKEDIN}" rel="noopener" target="_blank">{LINKEDIN_SVG} LinkedIn</a>
      </div>
      <div><h4>Products</h4><ul>
        <li><a href="tradeflo.html">TradeFlo</a></li><li><a href="careflo.html">CareFlo</a></li>
        <li><a href="healthflo.html">HealthFlo</a></li><li><a href="pricing.html">Pricing</a></li></ul></div>
      <div><h4>Solutions</h4><ul>
        {"".join(f'<li><a href="{s["href"]}">{s["name"].split(" and ")[0] if s["key"] != "medical-billing" else "Medical billing"}</a></li>' for s in SOLUTIONS)}</ul></div>
      <div><h4>Company</h4><ul>
        <li><a href="about.html">About</a></li><li><a href="contact.html">Contact</a></li>
        <li><a href="security.html">Security</a></li><li><a href="resources.html">Resources</a></li></ul></div>
      <div><h4>Legal</h4><ul>
        <li><a href="privacy.html">Privacy Policy</a></li><li><a href="terms.html">Terms of Service</a></li></ul></div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>{YEAR}</span> NexFlo Cloud, Minnesota</span>
      <span>Questions? <a href="mailto:{INFO}">{INFO}</a></span>
    </div>
  </div>
</footer>'''


def layout(title, description, body, active="", slug="", bare=False):
    full_title = title if "NexFlo" in title else f"{title} | NexFlo Cloud"
    canonical = f"{SITE_URL}/{slug.removesuffix('.html')}" if slug and slug != "index.html" else f"{SITE_URL}/"
    header = nav_html(active) if not bare else (
        '<header class="site-header"><nav class="container nav"><a class="brand" href="index.html">'
        '<img src="assets/logo.png" alt="NexFlo Cloud" width="154" height="46"></a>'
        '<div style="margin-left:auto"><a class="nav-login" href="index.html">← Back to nexflo.cloud</a></div></nav></header>')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="NexFlo Cloud">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#006BFD">
<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/styles.css">
<!-- Analytics: paste your snippet here (e.g. Plausible, GA4, Microsoft Clarity) -->
</head>
<body>
{header}
<main id="main">
{body}
</main>
{footer_html() if not bare else ""}
<script src="assets/main.js" defer></script>
</body>
</html>
'''


HONEYPOT = '<div class="hp" aria-hidden="true"><input type="text" name="website" tabindex="-1" autocomplete="off"></div>'


def signup_inline(source, dark=False, button="Get early access", product=""):
    prod = f'<input type="hidden" name="product" value="{product}">' if product else ""
    return f'''<form class="signup{" dark" if dark else ""}" data-form="Early access" data-to="{SALES}" novalidate>
  {HONEYPOT}<input type="hidden" name="source" value="{source}">{prod}
  <input type="email" name="email" placeholder="Work email" aria-label="Work email" required autocomplete="email">
  <button class="btn btn-primary" type="submit">{button}</button>
</form>
<p class="inline-success">✓ You're on the list. We'll be in touch from {SALES}.</p>'''


def page_hero(title, lead, eyebrow="", crumbs=None, actions="", badge=""):
    crumb = ""
    if crumbs:
        crumb = '<div class="breadcrumbs">' + " / ".join(
            f'<a href="{h}">{t}</a>' if h else t for t, h in crumbs) + "</div>"
    eb = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    return f'''<section class="page-hero"><div class="container">
  {crumb}<div class="row" style="gap:14px;margin-bottom:6px">{eb}{badge}</div>
  <h1>{title}</h1><p class="lead">{lead}</p>
  {f'<div class="actions">{actions}</div>' if actions else ""}
</div></section>'''


def cta_band(title="Get early access", text="Founding customers lock in launch pricing. Join the list and we'll reach out personally.",
             source="cta", product="", secondary=True):
    sec = (f'<p class="small">Prefer to talk numbers first? <a href="pricing.html#quote">Request pricing</a> '
           f'or <a href="demo.html">book a demo</a>.</p>') if secondary else ""
    return f'''<section class="cta-band"><div class="container"><div class="cta-box">
  <div><h2>{title}</h2><p class="mb-0">{text}</p></div>
  <div>{signup_inline(source, dark=True, product=product)}{sec}</div>
</div></div></section>'''


def product_cards(link_label="Learn more"):
    cards = []
    for p in PRODUCTS:
        feat = " featured" if p["status"] == "live" else ""
        first = '<span class="badge badge-blue">First to launch</span>' if p["status"] == "live" else status_badge(p["status"])
        cards.append(f'''<a class="card{feat}" href="{p["href"]}">
  <div class="card-top"><div class="product-mark">{p["mark"]}<span>Flo</span></div>{first}</div>
  <p>{p["line"]}</p><span class="more arrow">{link_label}</span></a>''')
    return f'<div class="grid grid-3">{"".join(cards)}</div>'


def faq(items):
    return '<div class="faq">' + "".join(
        f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items) + "</div>"


def opt(values, placeholder="Select…"):
    return f'<option value="" disabled selected>{placeholder}</option>' + "".join(f"<option>{v}</option>" for v in values)


PRODUCT_OPTS = ["TradeFlo", "CareFlo", "HealthFlo", "Not sure yet"]
VOLUME_OPTS = ["Under 100", "100 – 1,000", "1,000 – 10,000", "10,000 – 50,000", "50,000+", "Not sure"]


def form_success(title, text):
    return f'<div class="form-success" role="status"><div class="tick">✓</div><h3>{title}</h3><p class="muted">{text}</p></div>'


# ---------------------------------------------------------------- pages
PAGES = {}


def page(slug, title, description, active=""):
    def deco(fn):
        PAGES[slug] = (title, description, active, fn)
        return fn
    return deco


@page("index.html", "NexFlo Cloud — Less friction. More flow.",
      "Simpler EDI for growing businesses. NexFlo Cloud translates and exchanges your EDI documents with transparent pricing and simple onboarding.")
def home():
    why = [
        ("tag", "Transparent pricing", "Usage-based plans you can understand, typically well below legacy EDI providers. No surprise fees."),
        ("rocket", "Simple onboarding", "We help connect your first trading partner and walk you through every step."),
        ("code", "Modern integrations", "Use a REST API with clean JSON, or keep it simple with SFTP. Your choice."),
        ("chat", "A team that answers", "You talk directly to the people building the product. No ticket queues."),
    ]
    who = [s for s in SOLUTIONS]
    standards = [("X12", "TradeFlo"), ("EDIFACT", "TradeFlo"), ("HIPAA X12", "Planned"), ("HL7 v2", "Planned"), ("FHIR", "Planned")]
    return f'''
<section class="hero"><div class="container hero-grid">
  <div>
    <span class="pill-label">Coming soon · Early access open</span>
    <h1>Less friction.<br><span class="accent">More flow.</span></h1>
    <p class="sub">Simpler EDI for growing businesses.</p>
    {signup_inline("home-hero")}
    <p class="hero-note">Founding customers lock in launch pricing. <a class="journey" href="{LINKEDIN}" target="_blank" rel="noopener">Follow our journey →</a></p>
  </div>
  <img class="hero-art" src="assets/hero-cloud.jpg" alt="A glass cloud wrapped in flowing blue ribbons" width="1254" height="570">
</div></section>

<section class="section-soft" id="products"><div class="container">
  <div class="section-head"><span class="eyebrow">What we do</span>
    <h2>One platform for the documents your business runs on</h2>
    <p class="lead">We start with retail and supply chain EDI, then extend the same translation engine to healthcare.</p></div>
  {product_cards()}
</div></section>

<section id="how-it-works"><div class="container">
  <div class="section-head"><span class="eyebrow">How it works</span>
    <h2>From purchase order to payment, without the busywork</h2>
    <p class="lead">Say Walmart sends you a purchase order. Here's what happens with NexFlo.</p></div>
  <div class="steps">
    <div class="step"><h3>Connect your systems</h3><p>Link your trading partners and your ERP, spreadsheet or storefront through SFTP or our API. We help set up the first connection.</p></div>
    <div class="step"><h3>We translate and exchange</h3><p>Walmart's 850 purchase order arrives and becomes clean JSON your systems can read. Your invoice goes back as a correct 810.</p></div>
    <div class="step"><h3>Track it in one dashboard</h3><p>See every document, acknowledgment and error in one place, with alerts when something needs your attention.</p></div>
  </div>
  {translate_demo("Walmart purchase order", "X12 850", PO_X12, "What your system receives", "JSON", PO_JSON)}
</div></section>

<section class="section-soft"><div class="container">
  <div class="section-head center"><span class="eyebrow">Why NexFlo</span>
    <h2>Enterprise-grade EDI, minus the enterprise overhead</h2></div>
  <div class="feature-grid" style="grid-template-columns:repeat(4,1fr)">
    {"".join(f'<div class="feature">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in why)}
  </div>
</div></section>

<section><div class="container">
  <div class="section-head"><span class="eyebrow">Who it's for</span>
    <h2>Built for teams that trade data with bigger partners</h2></div>
  <div class="grid grid-4">
    {"".join(f'<a class="card" href="{s["href"]}">{icon(s["icon"])}<h3 class="mt-2">{s["name"]}</h3><p>{s["short"]}</p><span class="more arrow">{s["product"]}</span></a>' for s in who)}
  </div>
</div></section>

<section class="section-soft"><div class="container split">
  <div><span class="eyebrow">Standards we support</span>
    <h2>Speak your partners' language</h2>
    <p class="lead">TradeFlo handles retail and supply chain standards first. Healthcare standards are planned for CareFlo and HealthFlo in 2027.</p></div>
  <div class="chips">
    {"".join(f'<span class="chip{" ready" if l == "TradeFlo" else ""}">{n}<small>{l}</small></span>' for n, l in standards)}
  </div>
</div></section>

<section><div class="container founders">
  <div><span class="eyebrow">Founders</span>
    <h2>A father-and-son team in Minnesota</h2>
    <p class="lead">We started NexFlo because growing businesses deserve the same integration tools as big enterprises, without the price tag or the runaround.</p>
    <blockquote class="mt-3">When you contact NexFlo, you talk to the people building the product.</blockquote>
    <p class="mt-3"><a class="arrow" href="about.html">Read our story </a></p></div>
  <div class="founder-cards">
    <div class="founder"><div class="avatar">AB</div><h3>Aadith Balaji</h3><p>Co-founder</p></div>
    <div class="founder"><div class="avatar">BT</div><h3>Balaji Thiagarajan</h3><p>Co-founder</p><p style="margin-top:6px;font-size:.8rem">Also leads TechDigital Corporation</p></div>
  </div>
</div></section>

{cta_band("Get early access", "TradeFlo opens to founding customers first. Founding customers lock in launch pricing.", "home-cta")}
'''


@page("products.html", "Products", "TradeFlo, CareFlo and HealthFlo: EDI and healthcare data translation from NexFlo Cloud.", "products")
def products():
    return page_hero("Products", "One translation engine, three products. TradeFlo is first to launch; CareFlo and HealthFlo follow in 2027.",
                     "NexFlo Cloud", [("Home", "index.html"), ("Products", None)]) + f'''
<section><div class="container">{product_cards("See product")}</div></section>
<section class="section-soft"><div class="container split">
  <div><h2>Shared by every product</h2><p class="lead">Each product runs on the same core, so what you learn in one carries over.</p></div>
  <ul class="checks">
    <li>Translation to and from clean JSON</li><li>API and SFTP connections</li>
    <li>Partner management and transaction tracking</li><li>Validation and error alerts</li>
    <li>One dashboard and one team to talk to</li></ul>
</div></section>
{cta_band(source="products")}'''


def product_page(name, mark, status, lead, who, example_intro, demo, features, standards_label, standards, cta, notice="", product=""):
    badge = status_badge(status)
    is_live = status == "live"
    actions = (f'<a class="btn btn-primary btn-lg" href="early-access.html?product={name}">Get early access</a>'
               f'<a class="btn btn-secondary btn-lg" href="pricing.html?product={name}#quote">Request pricing</a>') if is_live else (
               f'<a class="btn btn-primary btn-lg" href="#waitlist">Join the waitlist</a>')
    feat_html = "".join(f'<div class="feature">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in features)
    who_html = "".join(f"<li>{w}</li>" for w in who)
    std_html = "".join(f'<span class="doc-chip" title="{d}">{c}</span>' for c, d in standards)
    std_rows = "".join(f'<tr><td><span class="doc-chip">{c}</span></td><td>{d}</td></tr>' for c, d in standards)
    title_html = f'{mark}<span style="color:var(--blue)">Flo</span>'
    cta_html = cta_band(*cta, product=name, secondary=is_live)
    return page_hero(title_html, lead, "", [("Products", "products.html"), (name, None)], actions, badge) + f'''
<section><div class="container split top">
  <div><span class="eyebrow">What it does</span><h2>{example_intro[0]}</h2><p class="lead">{example_intro[1]}</p>{notice}</div>
  <div class="card"><h3>Who it's for</h3><ul class="checks mt-2">{who_html}</ul></div>
</div></section>
<section class="section-soft"><div class="container">
  <div class="section-head"><span class="eyebrow">Example</span><h2>{demo[0]}</h2><p class="lead">{demo[1]}</p></div>
  {demo[2]}
</div></section>
<section><div class="container">
  <div class="section-head"><span class="eyebrow">Features</span><h2>{"What's included" if is_live else "What we're building"}</h2></div>
  <div class="feature-grid">{feat_html}</div>
</div></section>
<section class="section-soft"><div class="container split top">
  <div><span class="eyebrow">{standards_label}</span><h2>Supported {"documents" if name == "TradeFlo" else "standards" if name == "HealthFlo" else "transactions"}</h2>
    <p class="lead">{"" if is_live else "Planned for launch in 2027."}</p><div class="chips">{std_html}</div></div>
  <div class="card table-wrap"><table class="article" style="margin:0;max-width:none"><tbody>{std_rows}</tbody></table></div>
</div></section>
<div id="waitlist"></div>
{cta_html}'''


@page("tradeflo.html", "TradeFlo — EDI for suppliers and manufacturers",
      "TradeFlo translates X12 and EDIFACT documents like 850, 810 and 856 into clean JSON, with SFTP, API and transaction tracking.", "products")
def tradeflo():
    return product_page(
        "TradeFlo", "Trade", "live",
        "EDI for manufacturers, distributors and retail suppliers. Receive orders, send invoices and ship notices, and keep every retail partner happy.",
        ["Manufacturers selling to big-box retailers", "Distributors and wholesalers with many trading partners",
         "Retail and e-commerce suppliers facing new EDI requirements", "Teams outgrowing expensive legacy EDI providers"],
        ("Retailer EDI, translated into something your systems understand",
         "TradeFlo receives your partners' EDI documents, turns them into clean JSON or files your systems can use, and sends your responses back in the exact format each partner expects."),
        ("A Walmart purchase order, start to finish",
         "An 850 arrives from Walmart. TradeFlo validates it, sends the 997 acknowledgment, and hands your system clean JSON. When you ship, your 856 and 810 go back the same way.",
         translate_demo("Walmart purchase order", "X12 850", PO_X12, "Delivered to your system", "JSON", PO_JSON)),
        [("swap", "X12 and EDIFACT translation", "Read and write the standards your retail and international partners use."),
         ("code", "EDI to JSON", "Work with clean, documented JSON instead of segments and delimiters."),
         ("server", "SFTP", "Drop and pick up files from a secure SFTP folder. No code required."),
         ("plug", "REST API", "Send and receive documents programmatically and connect your ERP or storefront."),
         ("users", "Trading partner management", "Keep each partner's IDs, specs and connection settings in one place."),
         ("eye", "Transaction tracking", "Follow every document from received to acknowledged, with full history."),
         ("bell", "Error alerts", "Get notified about rejected or late documents before they become chargebacks."),
         ("check", "Validation", "Catch missing fields and bad values before a document leaves your hands."),
         ("chat", "Hands-on onboarding", "We help you connect your first trading partner, directly.")],
        "X12 documents",
        [("850", "Purchase order"), ("855", "Purchase order acknowledgment"), ("856", "Advance ship notice (ASN)"),
         ("810", "Invoice"), ("846", "Inventory inquiry / advice"), ("997", "Functional acknowledgment")],
        ("Get early access to TradeFlo", "Founding customers lock in launch pricing and help shape the product.", "tradeflo"),
    )


@page("careflo.html", "CareFlo — Healthcare claims and eligibility translation",
      "CareFlo is a planned HIPAA X12 translation layer for claims, eligibility, claim status and remittance. Coming 2027.", "products")
def careflo():
    notice = ('<div class="notice mt-3"><div><strong>Integration and translation come first.</strong> CareFlo is the layer that '
              'translates and validates your HIPAA X12 transactions. Payer connectivity is arranged separately, through your '
              'existing clearinghouse or a partner we help you set up.</div></div>')
    return product_page(
        "CareFlo", "Care", "soon",
        "Healthcare claims and eligibility translation, built for medical billing and revenue cycle teams. Coming 2027. Join the waitlist.",
        ["Medical billing companies", "Revenue cycle management (RCM) teams", "Practice management software vendors",
         "Clinics that manage their own billing"],
        ("Claims and eligibility data, in a format your team can work with",
         "CareFlo is built to translate HIPAA X12 transactions into clean JSON and back, validate them before they go out, and track each one through its lifecycle."),
        ("A clinic claim, translated",
         "A clinic's 837P professional claim becomes structured data your billing system can read, validate and monitor.",
         translate_demo("Clinic claim", "X12 837P", CLAIM_X12, "Structured claim", "JSON", CLAIM_JSON)),
        [("swap", "HIPAA X12 translation", "Planned support for the 5010 transaction sets billing teams use daily."),
         ("doc", "Claims", "Build and read 837 professional and institutional claims."),
         ("check", "Eligibility", "Translate 270/271 eligibility requests and responses."),
         ("eye", "Claim status", "Read 276/277 claim status updates in plain fields."),
         ("chart", "Remittance", "Turn 835 remittance advice into data you can reconcile against."),
         ("bell", "Validation and monitoring", "Catch errors before submission and get alerted when something stalls.")],
        "HIPAA X12 · planned",
        [("837", "Health care claim (professional / institutional)"), ("835", "Claim payment / remittance advice"),
         ("270/271", "Eligibility inquiry and response"), ("276/277", "Claim status request and response"),
         ("278", "Prior authorization / referral")],
        ("Join the CareFlo waitlist", "We'll let you know as soon as CareFlo opens, and early waitlist members get first access.", "careflo"),
        notice=notice,
    )


@page("healthflo.html", "HealthFlo — HL7 and FHIR data exchange",
      "HealthFlo is a planned HL7 v2 and FHIR integration product for health tech and hospital systems. Coming 2027.", "products")
def healthflo():
    return product_page(
        "HealthFlo", "Health", "soon",
        "HL7 v2 and FHIR data exchange, built for health tech teams and hospital systems. Coming 2027. Join the waitlist.",
        ["Health tech startups integrating with EHRs", "Hospital and clinic IT teams", "Digital health platforms",
         "Labs and imaging providers"],
        ("Connect clinical systems that speak different formats",
         "HealthFlo is built to map, route and monitor clinical messages between systems, so an HL7 v2 feed from one system can become FHIR resources for another."),
        ("Hospital data exchange, mapped",
         "An HL7 v2 admission message from a hospital system becomes a FHIR Patient resource a modern app can use.",
         translate_demo("Hospital admission", "HL7 v2 ADT^A01", HL7_MSG, "FHIR resource", "Patient", FHIR_JSON, mid="Map")),
        [("swap", "HL7 v2", "Planned parsing and generation for common message types like ADT, ORM and ORU."),
         ("code", "FHIR", "Work with FHIR R4 resources over a modern API."),
         ("route", "Data mapping", "Map fields between formats with reusable, versioned mappings."),
         ("map", "Message routing", "Send each message to the right destination based on its content."),
         ("eye", "Monitoring", "See message flow, failures and retries in one dashboard."),
         ("bell", "Alerts", "Get notified when an interface stops sending or starts failing.")],
        "Healthcare standards · planned",
        [("HL7 v2", "Event-based messages (ADT, ORM, ORU and more)"), ("FHIR R4", "Modern REST-based healthcare resources")],
        ("Join the HealthFlo waitlist", "We'll let you know as soon as HealthFlo opens, and early waitlist members get first access.", "healthflo"),
    )


@page("solutions.html", "Solutions", "EDI and healthcare data solutions for manufacturers, logistics, medical billing and health tech teams.", "solutions")
def solutions():
    cards = "".join(
        f'<a class="card" href="{s["href"]}">{icon(s["icon"])}<h3 class="mt-2">{s["name"]}</h3><p>{s["short"]}</p>'
        f'<span class="more arrow">Uses {s["product"]}</span></a>' for s in SOLUTIONS)
    return page_hero("Solutions for your industry", "Start with who you are. We'll show you which product fits.",
                     "Solutions", [("Home", "index.html"), ("Solutions", None)]) + f'''
<section><div class="container"><div class="grid grid-2">{cards}</div></div></section>
{cta_band(source="solutions")}'''


SOLUTION_CONTENT = {
    "manufacturers": dict(
        title="EDI that keeps retailers happy, at a price that makes sense",
        lead="Your retail partners require EDI. Your current options are expensive, slow to set up, or both. NexFlo is built to fix that.",
        pains=[("Retailers require EDI to do business", "Big-box and online retailers won't place orders without 850s, 856s and 810s in their exact format."),
               ("Legacy providers are expensive", "Per-partner fees, setup charges and long contracts add up fast for a growing manufacturer."),
               ("Mistakes cost you chargebacks", "A late or incorrect ship notice can mean fines and short payments from your retail partners.")],
        how="TradeFlo translates your partners' documents into clean data, sends your responses in the right format, and alerts you before small errors turn into chargebacks.",
        product="tradeflo"),
    "logistics": dict(
        title="Many trading partners. One place to manage them.",
        lead="Distributors and logistics teams juggle documents from dozens of partners, each with its own quirks. NexFlo brings them into one flow.",
        pains=[("Every partner is different", "Each customer and supplier has its own specs, IDs and connection method."),
               ("Too much manual handling", "Re-keying orders and ship notices from emails and portals burns hours and invites errors."),
               ("No single view of what's moving", "When documents live in different inboxes and portals, nobody knows what's stuck.")],
        how="TradeFlo keeps every trading partner's settings in one place, automates document exchange over SFTP or API, and tracks every transaction in one dashboard.",
        product="tradeflo"),
    "medical-billing": dict(
        title="Claims and eligibility data, in one consistent format",
        lead="Billing and RCM teams handle claims, eligibility checks and remittances across many payers. CareFlo is being built to simplify the data layer underneath.",
        pains=[("Every payer behaves differently", "Companion guides, edits and responses vary from one payer to the next."),
               ("Raw X12 is hard to work with", "837s, 835s and 271s are dense and hard to debug without specialist tools."),
               ("Errors surface too late", "Rejections show up days later, after the claim has already left your hands.")],
        how="CareFlo is planned as a translation and validation layer for HIPAA X12 transactions, turning them into clean JSON and catching errors early. Payer connectivity is arranged separately through your clearinghouse.",
        product="careflo"),
    "health-tech": dict(
        title="Connect systems that format data differently",
        lead="Health tech teams spend months on integrations because every EHR and hospital system speaks its own dialect. HealthFlo is being built to shorten that.",
        pains=[("Every integration is custom", "Each hospital's HL7 feed has its own quirks, even for the same message type."),
               ("Old and new standards mix", "You need to work with HL7 v2 feeds and FHIR APIs at the same time."),
               ("Interfaces fail quietly", "When a feed stops, you often hear about it from a customer first.")],
        how="HealthFlo is planned to map HL7 v2 to FHIR and back, route messages to the right place, and monitor every interface so you know about problems first.",
        product="healthflo"),
}


def solution_page(key):
    s = next(x for x in SOLUTIONS if x["key"] == key)
    c = SOLUTION_CONTENT[key]
    p = next(x for x in PRODUCTS if x["key"] == c["product"])
    live = p["status"] == "live"
    pains = "".join(f'<div class="pain"><span class="num">{i}</span><div><h3>{t}</h3><p class="muted mb-0">{d}</p></div></div>'
                    for i, (t, d) in enumerate(c["pains"], 1))
    return page_hero(c["title"], c["lead"], s["name"], [("Solutions", "solutions.html"), (s["name"], None)]) + f'''
<section><div class="container">
  <div class="section-head"><span class="eyebrow">Sound familiar?</span><h2>The problems we hear most</h2></div>
  <div class="grid grid-3">{pains}</div>
</div></section>
<section class="section-soft"><div class="container split">
  <div><span class="eyebrow">The fit</span><h2>{p["name"]} {status_badge(p["status"])}</h2><p class="lead">{c["how"]}</p>
    <div class="row mt-3"><a class="btn btn-secondary" href="{p["href"]}">Explore {p["name"]}</a>
    {f'<a class="btn btn-ghost arrow" href="pricing.html?product={p["name"]}#quote">Request pricing </a>' if live else ""}</div></div>
  <a class="card featured" href="{p["href"]}"><div class="card-top"><div class="product-mark">{p["mark"]}<span>Flo</span></div>{status_badge(p["status"])}</div><p>{p["line"]}</p><span class="more arrow">Learn more</span></a>
</div></section>
{cta_band("Get early access" if live else f"Join the {p['name']} waitlist",
          "Founding customers lock in launch pricing." if live else "Be first to know when it opens in 2027.",
          f"solution-{key}", product=p["name"], secondary=live)}'''


for _s in SOLUTIONS:
    page(_s["href"], _s["name"], f'{_s["short"]} NexFlo Cloud for {_s["name"].lower()}.', "solutions")(
        (lambda k: (lambda: solution_page(k)))(_s["key"]))


PRICING_FAQ = [
    ("Are there setup fees?", "Our goal is no surprise fees. Any onboarding cost is quoted upfront, in writing, before you sign anything."),
    ("How long are contracts?", "We plan to offer month-to-month and annual options. Founding customers won't be locked into multi-year terms."),
    ("How fast will you respond to my request?", "Within one business day. You'll hear from a founder, not an automated sequence."),
    ("What does early access mean?", "TradeFlo is opening to a small group of founding customers first. You get hands-on onboarding, direct access to the team, and a say in what we build next."),
    ("Do founding customers lock in launch pricing?", "Yes. Founding customers keep their launch pricing as the product grows."),
    ("When will prices be published?", "Once early access wraps up. Until then, every quote is tailored to your volume and partners."),
]


@page("pricing.html", "Pricing", "Transparent, usage-based EDI plans, typically well below legacy EDI providers. Request a quote from NexFlo Cloud.", "pricing")
def pricing():
    incl = {
        "TradeFlo": ["X12 and EDIFACT translation", "EDI to JSON", "SFTP and REST API", "Trading partner management", "Transaction tracking and error alerts", "Hands-on onboarding"],
        "CareFlo": ["HIPAA X12 translation (planned)", "Claims, eligibility, claim status, remittance", "Pre-submission validation", "Monitoring and alerts", "Works alongside your clearinghouse"],
        "HealthFlo": ["HL7 v2 and FHIR (planned)", "Data mapping", "Message routing", "Interface monitoring", "Alerts"],
    }
    cards = []
    for p in PRODUCTS:
        live = p["status"] == "live"
        btn = (f'<a class="btn btn-primary" href="?product={p["name"]}#quote" data-product="{p["name"]}">Request pricing</a>' if live
               else f'<a class="btn btn-secondary" href="?product={p["name"]}#quote" data-product="{p["name"]}">Join the waitlist</a>')
        cards.append(f'''<div class="card price-card{" featured" if live else ""}">
  <div class="card-top"><div class="product-mark">{p["mark"]}<span>Flo</span></div>{status_badge(p["status"])}</div>
  <p>{p["line"]}</p>
  <div class="price">{"Usage-based" if live else "Coming 2027"} <small>{"· quote on request" if live else ""}</small></div>
  <ul class="checks">{"".join(f"<li>{x}</li>" for x in incl[p["name"]])}</ul>{btn}</div>''')
    return page_hero("Transparent, usage-based plans, typically well below legacy EDI providers.",
                     "Prices aren't published during early access. Tell us about your volume and partners and we'll send a quote within one business day.",
                     "Pricing", [("Home", "index.html"), ("Pricing", None)]) + f'''
<section><div class="container"><div class="grid grid-3">{"".join(cards)}</div></div></section>

<section class="section-soft" id="quote"><div class="container split top">
  <div><span class="eyebrow">Request pricing</span><h2>Get a quote</h2>
    <p class="lead">A few details help us size your plan accurately. We'll reply from {SALES} within one business day.</p>
    <ul class="checks mt-4"><li>No obligation, no sales sequence</li><li>Founding customers lock in launch pricing</li><li>Talk directly to a founder</li></ul></div>
  <form class="form-card" data-form="Pricing request" data-to="{SALES}">
    {HONEYPOT}
    <div class="form-body"><div class="form-grid">
      <div class="field"><label for="q-name">Name</label><input id="q-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="q-email">Work email</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field"><label for="q-company">Company</label><input id="q-company" name="company" required autocomplete="organization"></div>
      <div class="field"><label for="q-product">Product of interest</label><select id="q-product" name="product" required>{opt(PRODUCT_OPTS)}</select></div>
      <div class="field"><label for="q-volume">Documents or transactions per month</label><select id="q-volume" name="monthly_volume" required>{opt(VOLUME_OPTS)}</select></div>
      <div class="field"><label for="q-provider">Current EDI provider <span class="opt">(if any)</span></label><input id="q-provider" name="current_provider" placeholder="e.g. none yet"></div>
      <div class="field full"><label for="q-notes">Anything else? <span class="opt">(optional)</span></label><textarea id="q-notes" name="notes" placeholder="Trading partners, systems you use, timelines…"></textarea></div>
    </div>
    <div class="form-foot"><small>By submitting you agree to our <a href="privacy.html">Privacy Policy</a>.</small><button class="btn btn-primary" type="submit">Request pricing</button></div></div>
    {form_success("Thanks, we've got it.", f"We'll send your quote from {SALES} within one business day.")}
  </form>
</div></section>

<section><div class="container narrow">
  <div class="section-head"><span class="eyebrow">FAQ</span><h2>Pricing questions</h2></div>
  {faq(PRICING_FAQ)}
</div></section>
{cta_band(source="pricing", secondary=False)}'''


GENERAL_FAQ = [
    ("What is NexFlo Cloud?", "NexFlo Cloud builds simpler EDI and healthcare data integration for growing businesses. TradeFlo, for retail and supply chain EDI, launches first."),
    ("When can I start using TradeFlo?", "TradeFlo is opening to founding customers through early access. Join the list and we'll reach out to schedule onboarding."),
    ("Do I need developers to use NexFlo?", "No. You can exchange files over SFTP and use the dashboard. Teams with developers can use the REST API and JSON instead."),
    ("Is CareFlo a clearinghouse?", "No. CareFlo is planned as a translation and validation layer. Payer connectivity is arranged separately, through your existing clearinghouse or a partner."),
    ("Are you HIPAA certified?", "There is no official HIPAA certification, and we don't make compliance claims we can't back up. See our <a href=\"security.html\">Security page</a> for our plans, including signing a Business Associate Agreement where applicable."),
    ("Where are you based?", "Minnesota. We're a father-and-son founding team, and you'll talk to us directly."),
]

GUIDES = [
    ("what-is-edi.html", "What is EDI?", "A plain-language introduction to electronic data interchange, X12 and why retailers require it.", "Guide · 6 min read"),
    ("837-835-transactions.html", "What are 837 and 835 transactions?", "How healthcare claims and remittances move between providers and payers.", "Guide · 5 min read"),
    ("retail-edi-documents.html", "The supplier's guide to retail EDI documents", "850, 855, 856, 810, 846 and 997, explained in the order they happen.", "Guide · 5 min read"),
]


@page("resources.html", "Resources", "Plain-language EDI guides, security information and answers to common questions from NexFlo Cloud.", "resources")
def resources():
    guide_cards = "".join(f'<a class="card" href="{h}"><span class="badge badge-blue">{m}</span><h3 class="mt-2">{t}</h3><p>{d}</p><span class="more arrow">Read guide</span></a>' for h, t, d, m in GUIDES)
    return page_hero("Resources", "Plain-language guides to EDI and healthcare data, plus answers to the questions we hear most.",
                     "Blog and guides", [("Home", "index.html"), ("Resources", None)]) + f'''
<section><div class="container">
  <div class="section-head"><h2>EDI guides</h2></div>
  <div class="grid grid-3">{guide_cards}</div>
</div></section>
<section class="section-soft"><div class="container grid grid-3">
  <a class="card" href="security.html">{icon("shield")}<h3 class="mt-2">Security</h3><p>How we plan to protect your data, and what we will and won't claim.</p><span class="more arrow">Read more</span></a>
  <div class="card">{icon("code")}<h3 class="mt-2">Developer docs</h3><p>API reference and integration guides.</p><span class="badge badge-soon mt-2">Coming later</span></div>
  <div class="card">{icon("doc")}<h3 class="mt-2">Changelog</h3><p>What's new in NexFlo, release by release.</p><span class="badge badge-soon mt-2">Coming later</span></div>
</div></section>
<section id="faq"><div class="container narrow">
  <div class="section-head"><span class="eyebrow">FAQ</span><h2>Frequently asked questions</h2></div>
  {faq(GENERAL_FAQ + PRICING_FAQ[:2])}
  <p class="mt-4 muted">Still have a question? <a href="contact.html">Contact us</a>.</p>
</div></section>
{cta_band(source="resources")}'''


def article(slug, title, desc, meta, body):
    @page(slug, title, desc, "resources")
    def _():
        return f'''<section class="page-hero"><div class="container article">
  <div class="breadcrumbs"><a href="resources.html">Resources</a> / Guides</div>
  <h1 style="font-size:clamp(2rem,4vw,3rem)">{title}</h1><p class="lead">{desc}</p><p class="meta">{meta}</p>
</div></section>
<section style="padding-top:56px"><div class="container"><div class="article">{body}
<hr style="border:0;border-top:1px solid var(--line);margin:48px 0 24px">
<p class="muted">More guides: {" · ".join(f'<a href="{h}">{t}</a>' for h, t, _, _ in GUIDES if h != slug)}</p>
</div></div></section>
{cta_band(source=slug.replace(".html", ""))}'''


article("what-is-edi.html", "What is EDI?",
        "A plain-language introduction to electronic data interchange, and why your retail partners require it.",
        "NexFlo Cloud · Guide", f'''
<p><strong>EDI (electronic data interchange)</strong> is a standard way for two companies' computer systems to exchange business documents, such as purchase orders, invoices and ship notices, without anyone retyping them.</p>
<p>Instead of emailing a PDF purchase order that someone keys into an order system, a retailer sends a structured file that your system can read automatically. You send back an invoice in the same structured way.</p>
<h2>Why do retailers require EDI?</h2>
<p>Large retailers handle millions of orders. Manual paperwork doesn't scale, so they require suppliers to trade documents in a standard format. If you want to sell to most big-box or national retailers, EDI is a condition of doing business.</p>
<h2>What does an EDI document look like?</h2>
<p>In North America the most common standard is <strong>ANSI X12</strong>. Each document is a "transaction set" with a number. A purchase order is an <strong>850</strong>. Here's a shortened example:</p>
{code_block("Purchase order", "X12 850", hl_edi(PO_X12))}
<p>Each line is a <em>segment</em>. The first few characters name the segment (for example <code>BEG</code> for the start of the order, <code>PO1</code> for a line item), and asterisks separate the values. It's compact for machines, but hard for people to read. That's the gap an EDI translator fills.</p>
<h2>What does an EDI translator do?</h2>
<ul><li><strong>Translates</strong> EDI into a format your systems understand, such as JSON or CSV, and back again.</li>
<li><strong>Validates</strong> documents against each partner's rules before they're sent.</li>
<li><strong>Exchanges</strong> files with your partners over secure connections like SFTP or AS2.</li>
<li><strong>Tracks</strong> every document and acknowledgment so nothing gets lost.</li></ul>
<h2>X12 vs. EDIFACT</h2>
<p><strong>X12</strong> is used mostly in North America. <strong>EDIFACT</strong> is the United Nations standard used widely in Europe and internationally. They carry the same kinds of business documents with different structures. TradeFlo is built to handle both.</p>
<h2>Getting started</h2>
<p>Most suppliers start with the documents their biggest retail partner requires, usually the 850, 856 and 810. See our <a href="retail-edi-documents.html">guide to retail EDI documents</a>, or <a href="tradeflo.html">learn how TradeFlo works</a>.</p>''')

article("837-835-transactions.html", "What are 837 and 835 transactions?",
        "How healthcare claims and remittances move between providers and payers, in plain language.",
        "NexFlo Cloud · Guide", f'''
<p>In U.S. healthcare, providers and insurers exchange billing data using <strong>HIPAA X12</strong> transactions, a set of EDI formats required under HIPAA's administrative simplification rules. The two you'll hear about most are the <strong>837</strong> and the <strong>835</strong>.</p>
<h2>The 837: the claim</h2>
<p>An <strong>837</strong> is a health care claim. A provider (or their billing company) sends it to a payer to request payment for services. There are three main variants:</p>
<table><thead><tr><th>Variant</th><th>Used for</th></tr></thead><tbody>
<tr><td>837P</td><td>Professional claims, such as physician office visits</td></tr>
<tr><td>837I</td><td>Institutional claims, such as hospital stays</td></tr>
<tr><td>837D</td><td>Dental claims</td></tr></tbody></table>
{code_block("Professional claim", "X12 837P", hl_edi(CLAIM_X12))}
<h2>The 835: the remittance</h2>
<p>An <strong>835</strong> is the electronic remittance advice. The payer sends it back to explain what was paid, what was adjusted and why. Billing teams use 835s to post payments and find denials to work.</p>
<h2>The rest of the family</h2>
<table><thead><tr><th>Transaction</th><th>What it does</th></tr></thead><tbody>
<tr><td>270 / 271</td><td>Eligibility inquiry and response: is this patient covered?</td></tr>
<tr><td>276 / 277</td><td>Claim status request and response: where is this claim?</td></tr>
<tr><td>278</td><td>Prior authorization and referral requests</td></tr>
<tr><td>999 / 277CA</td><td>Acknowledgments that a file or claim was received and accepted</td></tr></tbody></table>
<h2>Where does a clearinghouse fit?</h2>
<p>Most providers don't connect to each payer directly. A <strong>clearinghouse</strong> routes transactions to and from many payers. A translation layer, like the one we're building with <a href="careflo.html">CareFlo</a>, sits on your side: it turns these transactions into clean data your systems can use, validates them before they're sent, and tracks them. Payer connectivity is arranged separately.</p>''')

article("retail-edi-documents.html", "The supplier's guide to retail EDI documents",
        "850, 855, 856, 810, 846 and 997, explained in the order they happen.",
        "NexFlo Cloud · Guide", '''
<p>When you start selling to a large retailer, you'll get a list of required EDI documents. Here's what each one does, in the order you'll usually see them.</p>
<table><thead><tr><th>Document</th><th>Name</th><th>Who sends it</th></tr></thead><tbody>
<tr><td>846</td><td>Inventory inquiry / advice</td><td>You, to share stock levels</td></tr>
<tr><td>850</td><td>Purchase order</td><td>Retailer</td></tr>
<tr><td>997</td><td>Functional acknowledgment</td><td>Both: "we received your file"</td></tr>
<tr><td>855</td><td>PO acknowledgment</td><td>You: "we accept this order"</td></tr>
<tr><td>856</td><td>Advance ship notice (ASN)</td><td>You, before the shipment arrives</td></tr>
<tr><td>810</td><td>Invoice</td><td>You, to get paid</td></tr></tbody></table>
<h2>1. The order arrives (850)</h2>
<p>The retailer sends an 850 listing items, quantities, prices, ship-to locations and dates. Your system needs to read it quickly and accurately.</p>
<h2>2. Confirm receipt (997) and the order (855)</h2>
<p>A 997 tells the retailer you received the file. Many retailers also want an 855 confirming you accept the order, or noting changes such as backorders.</p>
<h2>3. Ship and notify (856)</h2>
<p>The 856 ASN tells the retailer exactly what's in each carton and pallet before it arrives. It's the document most likely to trigger chargebacks if it's late or wrong.</p>
<h2>4. Get paid (810)</h2>
<p>Your 810 invoice should match the order and the ASN. Mismatches slow down payment.</p>
<h2>How TradeFlo helps</h2>
<p><a href="tradeflo.html">TradeFlo</a> is built to handle all six documents, validate them against each partner's rules, and alert you before a problem becomes a chargeback.</p>''')


@page("security.html", "Security", "How NexFlo Cloud plans to protect your data: encryption, access control, monitoring and Business Associate Agreements.", "resources")
def security():
    items = [
        ("lock", "Encryption in transit", "All connections are planned to use TLS 1.2 or higher, including the dashboard, API and SFTP."),
        ("server", "Encryption at rest", "Stored documents and backups are planned to be encrypted at rest with AES-256."),
        ("key", "Access control", "Role-based access, multi-factor authentication and least-privilege access for our own team."),
        ("eye", "Audit logging", "A record of who accessed or changed what, available to you in the dashboard."),
        ("doc", "Data retention", "Clear, configurable retention so documents aren't kept longer than you need."),
        ("bell", "Monitoring", "Continuous monitoring for availability and unusual activity."),
    ]
    return page_hero("Security", "You're trusting us with business and, later, health data. Here's how we plan to protect it, and what we will and won't claim.",
                     "Trust", [("Resources", "resources.html"), ("Security", None)]) + f'''
<section><div class="container">
  <div class="section-head"><h2>Our security plans</h2><p class="lead">These are the controls we're building into NexFlo from day one. We'll update this page as each one is in place.</p></div>
  <div class="feature-grid">{"".join(f'<div class="feature">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in items)}</div>
</div></section>
<section class="section-soft"><div class="container split top">
  <div><span class="eyebrow">Healthcare</span><h2>Business Associate Agreements</h2>
    <p class="lead">For CareFlo and HealthFlo customers handling protected health information, we're prepared to sign a Business Associate Agreement (BAA) where applicable.</p></div>
  <div class="notice"><div><strong>What we don't claim.</strong> We don't claim HIPAA compliance certification or a SOC 2 report today. We'll only publish compliance claims once they're true and independently verified, and we'll list them here.</div></div>
</div></section>
<section><div class="container narrow center">
  <h2>Security questions?</h2><p class="lead">Ask us directly, or report a vulnerability, at <a href="mailto:{INFO}">{INFO}</a>.</p>
  <div class="row mt-3" style="justify-content:center"><a class="btn btn-primary" href="contact.html">Contact us</a></div>
</div></section>'''


@page("about.html", "About", "NexFlo Cloud is a father-and-son team in Minnesota building affordable, enterprise-grade integration for growing businesses.", "company")
def about():
    return page_hero("Enterprise-grade integration for growing businesses",
                     "NexFlo Cloud exists to make EDI and data integration affordable and simple for the businesses that big providers overlook.",
                     "About us", [("Company", None), ("About", None)]) + f'''
<section><div class="container split top">
  <div><span class="eyebrow">Our mission</span><h2>Less friction. More flow.</h2>
    <p class="lead">Growing businesses shouldn't have to choose between expensive legacy EDI providers and doing everything by hand. We're building the middle path: modern, transparent and easy to start.</p></div>
  <div><span class="eyebrow">Our story</span>
    <p>NexFlo started as a father-and-son project in Minnesota. Between us, we saw the same pattern again and again: small manufacturers and suppliers paying enterprise prices for EDI they barely understood, and waiting days for help when something broke.</p>
    <p>So we're building the product we wished existed. TradeFlo comes first, for suppliers and manufacturers trading with retailers. CareFlo and HealthFlo follow, bringing the same approach to healthcare data.</p>
    <p class="mb-0">Balaji also leads TechDigital Corporation, an IT consulting and talent firm in Burnsville, Minnesota, that has helped companies with technology projects since 2008. NexFlo brings that experience to a product: integration that works, explained plainly, with people you can reach.</p></div>
</div></section>
<section class="section-soft"><div class="container founders">
  <div><span class="eyebrow">The team</span><h2>Talk to the people building it</h2>
    <p class="lead">We're a small team on purpose. When you email us, a founder answers.</p>
    <div class="row mt-3"><a class="btn btn-primary" href="contact.html">Get in touch</a><a class="btn btn-secondary" href="demo.html">Book a demo</a></div></div>
  <div class="founder-cards">
    <div class="founder"><div class="avatar">AB</div><h3>Aadith Balaji</h3><p>Co-founder</p></div>
    <div class="founder"><div class="avatar">BT</div><h3>Balaji Thiagarajan</h3><p>Co-founder</p><p style="margin-top:6px;font-size:.8rem">Also leads TechDigital Corporation</p></div>
  </div>
</div></section>
<section><div class="container grid grid-3">
  <div class="card">{icon("map")}<h3 class="mt-2">Based in Minnesota</h3><p>Built in the Midwest, for businesses everywhere.</p></div>
  <div class="card">{icon("tag")}<h3 class="mt-2">Transparent by default</h3><p>Clear pricing and honest claims about what's built and what's planned.</p></div>
  <div class="card">{icon("chat")}<h3 class="mt-2">Direct support</h3><p>No ticket queues. You get the people who wrote the code.</p></div>
</div></section>
{cta_band(source="about")}'''


@page("contact.html", "Contact", "Contact the NexFlo Cloud team. We respond within one business day.", "company")
def contact():
    return page_hero("Contact us", "Questions, partnerships or just curious? We reply within one business day.",
                     "Company", [("Company", None), ("Contact", None)]) + f'''
<section><div class="container split top">
  <form class="form-card" data-form="Contact" data-to="{INFO}">
    {HONEYPOT}
    <div class="form-body"><div class="form-grid">
      <div class="field"><label for="c-name">Name</label><input id="c-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field full"><label for="c-company">Company <span class="opt">(optional)</span></label><input id="c-company" name="company" autocomplete="organization"></div>
      <div class="field full"><label for="c-msg">Message</label><textarea id="c-msg" name="message" required></textarea></div>
    </div>
    <div class="form-foot"><small>We'll reply within one business day.</small><button class="btn btn-primary" type="submit">Send message</button></div></div>
    {form_success("Message sent.", "Thanks for reaching out. We'll reply within one business day.")}
  </form>
  <div class="grid">
    <div class="card">{icon("chat")}<h3 class="mt-2">General questions</h3><p><a href="mailto:{INFO}">{INFO}</a></p></div>
    <div class="card">{icon("tag")}<h3 class="mt-2">Sales and pricing</h3><p><a href="mailto:{SALES}">{SALES}</a></p></div>
    <div class="card">{icon("map")}<h3 class="mt-2">Location</h3><p>Minnesota, USA</p></div>
  </div>
</div></section>'''


@page("demo.html", "Book a demo", "Book a demo of NexFlo Cloud and see how TradeFlo handles your EDI documents.")
def demo():
    return page_hero("Book a demo", "See TradeFlo with your own trading partners in mind. 30 minutes with a founder, no slides required.",
                     "Demo", [("Home", "index.html"), ("Book a demo", None)]) + f'''
<section><div class="container split top">
  <form class="form-card" data-form="Demo request" data-to="{SALES}">
    {HONEYPOT}
    <div class="form-body"><div class="form-grid">
      <div class="field"><label for="d-name">Name</label><input id="d-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="d-email">Work email</label><input id="d-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field"><label for="d-company">Company</label><input id="d-company" name="company" required autocomplete="organization"></div>
      <div class="field"><label for="d-role">Your role <span class="opt">(optional)</span></label><input id="d-role" name="role" autocomplete="organization-title"></div>
      <div class="field"><label for="d-product">Product of interest</label><select id="d-product" name="product" required>{opt(PRODUCT_OPTS)}</select></div>
      <div class="field"><label for="d-time">Best time to talk <span class="opt">(optional)</span></label><input id="d-time" name="preferred_time" placeholder="e.g. weekday afternoons CT"></div>
      <div class="field full"><label for="d-msg">What would you like to see? <span class="opt">(optional)</span></label><textarea id="d-msg" name="message" placeholder="Trading partners, documents, current setup…"></textarea></div>
    </div>
    <div class="form-foot"><small>By submitting you agree to our <a href="privacy.html">Privacy Policy</a>.</small><button class="btn btn-primary" type="submit">Request a demo</button></div></div>
    {form_success("Demo requested.", "We'll email you within one business day to find a time.")}
  </form>
  <div><h2>What we'll cover</h2>
    <ul class="checks mt-3"><li>Your trading partners and the documents they require</li><li>A live walk-through of an 850 to JSON translation</li>
      <li>How SFTP and API connections work</li><li>Onboarding timeline and early-access pricing</li></ul>
    <div class="notice mt-4"><div>Prefer email? Write to <a href="mailto:{SALES}">{SALES}</a>.</div></div></div>
</div></section>'''


def early_access_form(source):
    return f'''<form class="form-card" data-form="Early access" data-to="{SALES}">
    {HONEYPOT}<input type="hidden" name="source" value="{source}">
    <div class="form-body"><div class="form-grid">
      <div class="field"><label for="e-name">Name</label><input id="e-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="e-email">Work email</label><input id="e-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field"><label for="e-company">Company</label><input id="e-company" name="company" required autocomplete="organization"></div>
      <div class="field"><label for="e-product">Product of interest</label><select id="e-product" name="product" required>{opt(PRODUCT_OPTS)}</select></div>
      <div class="field full"><label for="e-partners">Who are your main trading partners? <span class="opt">(optional)</span></label><input id="e-partners" name="trading_partners" placeholder="e.g. Walmart, Target, Home Depot"></div>
    </div>
    <div class="form-foot"><small>By submitting you agree to our <a href="privacy.html">Privacy Policy</a>.</small><button class="btn btn-primary" type="submit">Get early access</button></div></div>
    {form_success("You're on the list.", f"We'll reach out personally from {SALES}. Founding customers lock in launch pricing.")}
  </form>'''


@page("early-access.html", "Get early access", "Join the NexFlo Cloud early-access list. Founding customers lock in launch pricing.")
def early_access():
    return page_hero("Get early access", "TradeFlo is opening to a small group of founding customers. CareFlo and HealthFlo waitlists are open too.",
                     "Early access", [("Home", "index.html"), ("Early access", None)]) + f'''
<section><div class="container split top">
  {early_access_form("early-access-page")}
  <div><h2>What founding customers get</h2>
    <ul class="checks mt-3"><li>Launch pricing, locked in</li><li>Hands-on onboarding for your first trading partner</li>
      <li>A direct line to the founders</li><li>A real say in what we build next</li></ul>
    <p class="mt-4 muted">Want numbers first? <a href="pricing.html#quote">Request pricing</a>.</p></div>
</div></section>'''


@page("portal.html", "Customer portal", "The NexFlo Cloud customer portal is coming soon.")
def portal():
    return f'''<div class="portal-wrap"><div class="container"><div class="portal-card form-card" style="margin:0 auto">
  <img src="assets/cloud-icon.png" alt="" width="88" height="55" style="margin:0 auto 20px">
  <span class="badge badge-soon">Coming soon</span>
  <h1 style="font-size:2rem;margin-top:14px">Customer portal coming soon</h1>
  <p class="muted">This is where you'll sign in to manage trading partners, track documents and see alerts. It opens with TradeFlo early access.</p>
  <div style="display:flex;justify-content:center;margin-top:24px">{signup_inline("portal")}</div>
  <p class="mt-4 muted" style="font-size:.9rem">Already a customer? Email <a href="mailto:{SALES}">{SALES}</a>.</p>
</div></div></div>'''


LEGAL_NOTE = ('<div class="notice" style="margin-bottom:32px"><div><strong>Draft.</strong> This is a starting template and must be '
              'reviewed by a qualified attorney before launch.</div></div>')


@page("privacy.html", "Privacy Policy", "How NexFlo Cloud collects and uses personal information.")
def privacy():
    return f'''<section class="page-hero"><div class="container article"><h1 style="font-size:2.6rem">Privacy Policy</h1><p class="meta">Last updated: November 6, 2026</p></div></section>
<section style="padding-top:48px"><div class="container"><div class="article">{LEGAL_NOTE}
<p>NexFlo Cloud ("NexFlo", "we", "us") respects your privacy. This policy explains what we collect on nexflo.cloud and how we use it.</p>
<h2>Information we collect</h2>
<ul><li><strong>Information you give us</strong> through forms: name, email address, company, role, product interest, estimated volumes, current EDI provider and any message you send.</li>
<li><strong>Usage information</strong> collected automatically, such as pages visited, browser type and approximate location, through privacy-respecting analytics.</li></ul>
<h2>How we use it</h2>
<ul><li>To respond to your requests, provide quotes and schedule demos</li><li>To send early-access and product updates you signed up for</li>
<li>To understand how the site is used and improve it</li></ul>
<p>We do not sell your personal information.</p>
<h2>Sharing</h2>
<p>We share information only with service providers that help us run the site and our business (for example, email and hosting providers), under contracts that limit their use of it, or when required by law.</p>
<h2>Retention</h2><p>We keep form submissions only as long as needed for the purposes above, or as required by law.</p>
<h2>Your choices</h2><p>You can unsubscribe from emails at any time and ask us to access, correct or delete your information by writing to <a href="mailto:{INFO}">{INFO}</a>.</p>
<h2>Security</h2><p>We use reasonable safeguards to protect your information. See our <a href="security.html">Security page</a>.</p>
<h2>Contact</h2><p>NexFlo Cloud, Minnesota, USA · <a href="mailto:{INFO}">{INFO}</a></p>
</div></div></section>'''


@page("terms.html", "Terms of Service", "Terms governing use of the NexFlo Cloud website.")
def terms():
    return f'''<section class="page-hero"><div class="container article"><h1 style="font-size:2.6rem">Terms of Service</h1><p class="meta">Last updated: November 6, 2026</p></div></section>
<section style="padding-top:48px"><div class="container"><div class="article">{LEGAL_NOTE}
<p>These terms govern your use of nexflo.cloud (the "Site"), operated by NexFlo Cloud. By using the Site you agree to them.</p>
<h2>Use of the Site</h2><p>You may use the Site for lawful purposes only. Don't attempt to disrupt it, access it without authorization, or misuse its forms.</p>
<h2>Early access and products</h2><p>Information about products, features and timelines describes our plans and may change. Features labeled "planned", "built for" or "coming" are not yet available. Use of NexFlo products will be governed by a separate customer agreement.</p>
<h2>Intellectual property</h2><p>The Site's content, logos and design belong to NexFlo Cloud. You may not copy or reuse them without permission.</p>
<h2>Disclaimers</h2><p>The Site is provided "as is" without warranties of any kind. Guides and articles are for general information and are not legal, compliance or professional advice.</p>
<h2>Limitation of liability</h2><p>To the extent permitted by law, NexFlo Cloud is not liable for indirect or consequential damages arising from use of the Site.</p>
<h2>Governing law</h2><p>These terms are governed by the laws of the State of Minnesota.</p>
<h2>Contact</h2><p><a href="mailto:{INFO}">{INFO}</a></p>
</div></div></section>'''


@page("404.html", "Page not found", "This page doesn't exist.")
def not_found():
    return '''<div class="portal-wrap"><div class="container center"><img src="assets/cloud-icon.png" alt="" width="96" height="60" style="margin:0 auto 20px"><span class="eyebrow">404</span><h1>Lost the flow?</h1>
<p class="lead">That page doesn't exist. Let's get you back on track.</p>
<div class="row mt-3" style="justify-content:center"><a class="btn btn-primary" href="index.html">Go home</a><a class="btn btn-secondary" href="contact.html">Contact us</a></div></div></div>'''


# ---------------------------------------------------------------- build
# On Vercel (VERCEL=1) links become clean root paths: "pricing.html#quote" -> "/pricing#quote".
# Locally they stay as .html files so dist/ can be opened straight from disk.
CLEAN_URLS = os.environ.get("VERCEL") == "1" or os.environ.get("CLEAN_URLS") == "1"


def clean_links(text):
    text = re.sub(r'(href|src)="assets/', r'\1="/assets/', text)
    text = re.sub(r'href="index\.html([#?][^"]*)?"', lambda m: f'href="/{m.group(1) or ""}"', text)
    return re.sub(r'href="([a-z0-9-]+)\.html([#?][^"]*)?"', lambda m: f'href="/{m.group(1)}{m.group(2) or ""}"', text)


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    bare = {"portal.html"}
    for slug, (title, desc, active, fn) in PAGES.items():
        out = layout(title, desc, fn(), active, slug, bare=slug in bare)
        if CLEAN_URLS:
            out = clean_links(out)
        (DIST / slug).write_text(out, encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if s == 'index.html' else s.removesuffix('.html')}</loc></url>" for s in PAGES if s not in ("404.html", "portal.html"))
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages into {DIST}")


if __name__ == "__main__":
    build()
