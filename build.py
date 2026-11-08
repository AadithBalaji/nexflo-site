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
DIST = ROOT / ("dist-lines" if __import__("os").environ.get("HERO") == "lines" else "dist")

# ---------------------------------------------------------------- settings
SITE_URL = "https://nexflo.cloud"
SALES = "aadithbalaji@nexflo.cloud"  # early access, pricing and demo requests
INFO = "support@nexflo.cloud"  # contact form, security, legal
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
    "folder": '<path d="M3 6a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><rect x="9.5" y="12" width="5" height="4" rx=".5"/><path d="M10.5 12v-1a1.5 1.5 0 0 1 3 0v1"/>',
    "sliders": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "cloud": '<path d="M7 18h10a4 4 0 0 0 .6-8A6 6 0 0 0 6.2 9.4 4.3 4.3 0 0 0 7 18z"/>',
}


def icon(name, cls="icon"):
    return (f'<span class="{cls}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg></span>')


CHEV = '<svg class="chev" viewBox="0 0 10 10" aria-hidden="true"><path d="M2 3.5l3 3 3-3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
LINKEDIN_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.4 2H3.6A1.6 1.6 0 0 0 2 3.6v16.8A1.6 1.6 0 0 0 3.6 22h16.8a1.6 1.6 0 0 0 1.6-1.6V3.6A1.6 1.6 0 0 0 20.4 2zM8 19H5V9h3zM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4zM19 19h-3v-4.9c0-1.2 0-2.7-1.6-2.7S12.5 12.7 12.5 14v5h-3V9h2.9v1.4c.4-.8 1.4-1.6 2.9-1.6 3.1 0 3.7 2 3.7 4.7z"/></svg>'

# ---------------------------------------------------------------- products & solutions data
PRODUCTS = [
    dict(key="tradeflo", name="TradeFlo", mark="Trade", href="tradeflo.html", status="live", sub="Business document exchange",
         line="Make it easier to send and receive purchase orders, invoices, and shipping information between your business and its partners.",
         **{"for": "manufacturers, distributors, retail suppliers and e-commerce sellers"}),
    dict(key="careflo", name="CareFlo", mark="Care", href="careflo.html", status="soon", sub="Healthcare billing and claims",
         line="Simplify how healthcare businesses exchange claims, billing information, and insurance-related documents.",
         **{"for": "medical billing companies, healthcare providers and revenue cycle teams"}),
    dict(key="healthflo", name="HealthFlo", mark="Health", href="healthflo.html", status="soon", sub="Healthcare system connections",
         line="Help healthcare software and medical systems exchange important information more easily.",
         **{"for": "hospitals, clinics, EHR vendors and digital health companies"}),
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
    return (f'<div class="code"><div class="code-head"><span class="dots"><i></i><i></i><i></i></span><b>{title}</b>'
            f'<span>{tag}</span></div><pre><code>{body}</code></pre></div>')


def translate_demo(left_title, left_tag, left_raw, right_title, right_tag, right_raw, mid="Translate", left_kind="edi",
                   done="Delivered as JSON"):
    left = hl_edi(left_raw) if left_kind == "edi" else hl_json(left_raw)
    return f'''<div class="translate" data-animate data-done="✓ {done}">
  {code_block(left_title, left_tag, left)}
  <div class="translate-mid"><div class="pill"><i>→</i>{mid}</div><div class="translate-status" aria-live="off"></div></div>
  {code_block(right_title, right_tag, hl_json(right_raw))}
</div>'''


def hl_shell(text):
    out = []
    for line in text.strip("\n").split("\n"):
        e = html.escape(line, quote=False)
        if e.lstrip().startswith("#"):
            out.append(f'<span class="c">{e}</span>')
            continue
        e = re.sub(r'"([^"]*)"', r'<span class="s">"\1"</span>', e)
        e = re.sub(r"^(\$|sftp&gt;|POST|GET)", r'<span class="k">\1</span>', e)
        e = re.sub(r"(\s)(-[A-Za-z])\b", r'\1<span class="k">\2</span>', e)
        out.append(e)
    return "\n".join(out)


API_CURL = """
# Send an invoice. NexFlo delivers it to Walmart as an X12 810.
curl https://api.nexflo.cloud/v1/documents \\
  -H "Authorization: Bearer $NEXFLO_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "partner": "walmart",
    "type": "invoice",
    "po_number": "4500018273",
    "lines": [{ "upc": "012345678905", "qty": 240, "unit_price": 4.85 }]
  }'

# 202 Accepted  ->  translated, validated, sent as 810
"""

API_SFTP = """
# No code? Drop files in a folder. We handle the EDI.
$ sftp acme@sftp.nexflo.cloud
sftp> put invoice_4500018273.csv /outbound/walmart/
Uploading invoice_4500018273.csv  100%

sftp> get /inbound/walmart/po_4500018274.json
Fetching po_4500018274.json  100%

# Every inbound order arrives as clean JSON or CSV.
"""

API_HOOK = """
{
  "event": "document.received",
  "partner": "walmart",
  "type": "purchase_order",
  "standard": "X12 850",
  "po_number": "4500018274",
  "received_at": "2026-11-07T14:02:11Z",
  "data_url": "https://api.nexflo.cloud/v1/documents/doc_8f2k"
}
"""


def api_tabs():
    panes = [("REST API", "curl", hl_shell(API_CURL)), ("SFTP", "shell", hl_shell(API_SFTP)),
             ("Webhook", "POST /your-endpoint", hl_json(API_HOOK))]
    tabs = "".join(f'<button class="tab" role="tab" aria-selected="{str(i == 0).lower()}">{t}</button>' for i, (t, _, _) in enumerate(panes))
    bodies = "".join(f'<div role="tabpanel"{"" if i == 0 else " hidden"}><pre><code>{b}</code></pre></div>' for i, (_, _, b) in enumerate(panes))
    return (f'<div class="code code-tabs" data-tabs><div class="code-head"><span class="dots"><i></i><i></i><i></i></span>'
            f'<div role="tablist" aria-label="Connection options">{tabs}</div><span>TradeFlo</span></div>{bodies}'
            f'<p class="api-note">API preview. Endpoint names may change before launch.</p></div>')


def dashboard_mock():
    return '''<div class="dash" data-dash aria-label="Dashboard preview with sample data">
  <div class="dash-top"><span class="dots"><i></i><i></i><i></i></span><span>app.nexflo.cloud / transactions</span><span class="badge">Illustration</span></div>
  <div class="dash-kpis">
    <div><small>Documents today</small><b data-kpi="docs">1,284</b></div>
    <div><small>Acknowledged</small><b>99.6%</b></div>
    <div><small>Needs review</small><b data-kpi="err">1</b></div>
  </div>
  <div class="dash-row head"><span>Time</span><span>Partner</span><span>Document</span><span>Status</span></div>
  <div data-rows></div>
</div>'''


TICKER = [
    ("850", "Purchase order", ""), ("855", "PO acknowledgment", ""), ("856", "Advance ship notice", ""), ("810", "Invoice", ""),
    ("846", "Inventory advice", ""), ("997", "Functional acknowledgment", ""), ("ORDERS", "EDIFACT order", ""),
    ("INVOIC", "EDIFACT invoice", ""), ("DESADV", "EDIFACT despatch advice", ""), ("837", "Health care claim", "2027"),
    ("835", "Remittance advice", "2027"), ("270/271", "Eligibility", "2027"), ("HL7", "v2 messages", "2027"), ("FHIR", "R4 resources", "2027"),
]


def ticker():
    one = "".join(f'<span><b>{c}</b>{n}{f"<i>{t}</i>" if t else ""}</span>' for c, n, t in TICKER)
    return (f'<div class="ticker" role="marquee" aria-label="Supported documents"><div class="ticker-track">'
            f'<div class="ticker-set">{one}</div><div class="ticker-set" aria-hidden="true">{one}</div></div></div>')


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
        <li class="nav-item"><a class="nav-link{act("company")}" href="about.html">About</a></li>
        <li class="nav-item"><a class="nav-link" href="contact.html">Contact</a></li>
      </ul>
      <div class="nav-actions">
        <a class="nav-login" href="{PORTAL_URL}">Portal login</a>
        <a class="btn btn-primary btn-sm" href="early-access.html">Join early access</a>
      </div>
    </div>
  </nav>
</header>'''


def footer_html():
    cols = [
        ("Products", [("TradeFlo", "tradeflo.html"), ("CareFlo", "careflo.html"), ("HealthFlo", "healthflo.html"), ("Pricing", "pricing.html"), ("Portal login", PORTAL_URL)]),
        ("Solutions", [(s["name"], s["href"]) for s in SOLUTIONS]),
        ("Resources", [("EDI guides", "resources.html"), ("What is EDI?", "what-is-edi.html"), ("837 and 835 explained", "837-835-transactions.html"), ("Security", "security.html"), ("FAQ", "resources.html#faq")]),
        ("Company", [("About", "about.html"), ("Contact", "contact.html"), ("Talk to us", "demo.html"), ("Join early access", "early-access.html")]),
    ]
    def col(h, links):
        items = "".join('<li><a href="%s">%s</a></li>' % (u, t) for t, u in links)
        return '<div class="foot-col"><h4>%s</h4><ul>%s</ul></div>' % (h, items)
    col_html = "".join(col(h, links) for h, links in cols)
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="foot-grid">
      <div class="foot-brand">
        <a href="index.html" aria-label="NexFlo Cloud home"><img src="assets/logo.png" alt="NexFlo Cloud" width="154" height="46"></a>
        <p>Minnesota, USA</p>
        <p><a href="mailto:{INFO}">{INFO}</a></p>
        <div class="foot-social"><a href="{LINKEDIN}" rel="noopener" target="_blank" aria-label="NexFlo on LinkedIn">{LINKEDIN_SVG}</a></div>
      </div>
      {col_html}
    </div>
    <div class="foot-bottom">
      <span>© <span data-year>{YEAR}</span> NexFlo Cloud · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a></span>
    </div>
  </div>
</footer>'''


def layout(title, description, body, active="", slug="", bare=False):
    full_title = title if "NexFlo" in title else f"{title} | NexFlo Cloud"
    canonical = f"{SITE_URL}/{slug.removesuffix('.html')}" if slug and slug != "index.html" else f"{SITE_URL}/"
    header = nav_html(active) if not bare else (
        '<header class="site-header"><nav class="container nav"><a class="brand" href="index.html">'
        '<img src="assets/logo.png" alt="NexFlo Cloud" width="154" height="46"></a>'
        '<div style="margin-left:auto"><a class="nav-login" href="index.html">← Back to site</a></div></nav></header>')
    return f'''<!doctype html>
<html lang="en" data-theme="dark">
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
<meta name="theme-color" content="#050B1A">
<link rel="icon" href="assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
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
<script src="assets/motion.js" defer></script>
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
    return f'''<section class="page-hero"><div class="arc ph-arc"></div><div class="container">
  {crumb}<div class="row" style="gap:14px;margin-bottom:6px">{eb}{badge}</div>
  <h1>{title}</h1><p class="lead">{lead}</p>
  {f'<div class="actions">{actions}</div>' if actions else ""}
</div></section>'''


def cta_band(title="Join early access", text="Founding customers keep their launch pricing. Join the list and the NexFlo team will reach out personally.",
             source="cta", product="", secondary=True):
    sec = (f'<p class="small">Have questions first? <a href="demo.html">Talk to us</a> '
           f'or <a href="pricing.html#quote">ask about pricing</a>.</p>') if secondary else ""
    return f'''<section class="cta2"><div class="container"><div class="cta2-box"><div class="arc"></div>
  <div><h2>{title}</h2><p>{text}</p></div>
  <div>{signup_inline(source, product=product)}{sec}</div>
</div></div></section>'''


def product_cards(link_label="Learn more"):
    rows = "".join(
        f'<a class="prow" href="{p["href"]}"><span class="prow-num">0{i}</span><span class="prow-name">{p["mark"]}<span>Flo</span></span>'
        f'<span class="prow-desc">{p["line"]}</span><span class="prow-status">{status_badge(p["status"])}</span>'
        f'<span class="prow-go" aria-hidden="true">→</span></a>' for i, p in enumerate(PRODUCTS, 1))
    return f'<div class="rows">{rows}</div>'


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


HERO_JSON = """
{
  "type": "purchase_order",
  "partner": "walmart",
  "po_number": "4500018273",
  "ship_to": "Walmart DC 6094",
  "item_upc": "012345678905",
  "quantity": 240,
  "unit_price": 4.85
}
"""

API_JS = """// Send an invoice. Walmart receives a valid X12 810.
const res = await fetch("https://api.nexflo.cloud/v1/documents", {
  method: "POST",
  headers: { Authorization: `Bearer ${NEXFLO_API_KEY}` },
  body: JSON.stringify({
    partner: "walmart",
    type: "invoice",
    po_number: "4500018273",
    lines: [{ upc: "012345678905", qty: 240, unit_price: 4.85 }],
  }),
});
// 202 Accepted: checked, translated, sent as an 810"""

SFTP_SESSION = """$ sftp acme@sftp.nexflo.cloud
sftp> put invoice_4500018273.csv /outbound/walmart/
Uploading invoice_4500018273.csv          100%
sftp> ls /inbound/walmart/
po_4500018274.csv    po_4500018275.csv
sftp> get /inbound/walmart/po_4500018274.csv
Fetching po_4500018274.csv                100%
sftp> bye"""


def hl_js(text):
    out = []
    for line in text.split("\n"):
        e = html.escape(line, quote=False)
        if e.lstrip().startswith("//"):
            out.append(f'<span class="c">{e}</span>')
            continue
        e = re.sub(r'("[^"]*"|`[^`]*`)', r'<span class="s">\1</span>', e)
        e = re.sub(r'\b(const|await|fetch|method|headers|body)\b', r'<span class="k">\1</span>', e)
        e = re.sub(r'(?<![\w">])(\d+(?:\.\d+)?)(?![\w"<])', r'<span class="n">\1</span>', e)
        out.append(e)
    return "\n".join(out)


def _lines(body):
    return "".join(f'<span class="ln">{l or " "}</span>' for l in body.split("\n"))


def win(name, meta, body, typing=False):
    """Code window with a filename tab and line numbers."""
    return (f'<div class="win"><div class="win-bar"><span class="tab-name">{name}</span>'
            f'<span class="win-meta">{meta}</span></div><div{" data-type" if typing else ""}><pre><code>{_lines(body)}</code></pre></div></div>')


def win_tabs(panes, note=""):
    """Code window with tabs. The first pane types itself out when scrolled into view."""
    tabs = "".join(f'<button class="win-tab" role="tab" aria-selected="{str(i == 0).lower()}">{t}</button>' for i, (t, _, _) in enumerate(panes))
    bodies = "".join(f'<div role="tabpanel"{" data-type" if i == 0 else " hidden"}><pre><code>{_lines(b)}</code></pre></div>' for i, (_, _, b) in enumerate(panes))
    foot = f'<p class="win-note">{note}</p>' if note else ""
    return f'<div class="win" data-tabs><div class="win-bar" role="tablist" aria-label="Ways to connect">{tabs}</div>{bodies}{foot}</div>'


def hero_demo():
    steps = "".join(f'<li>{t}<span>--:--:--</span></li>' for t in ("Received", "Checked", "Confirmed", "Delivered"))
    return f'''<div class="demo" data-demo aria-label="Illustration: a Walmart purchase order translated into plain data">
  <div class="demo-bar"><span class="tab-name">850_4500018273.x12</span><span>Illustration · sample order</span></div>
  <div class="demo-panes">
    <div class="demo-pane"><div class="demo-label">What Walmart sends · EDI purchase order</div><pre><code>{hl_edi(PO_X12)}</code></pre></div>
    <div class="demo-pane"><div class="demo-label">What your system gets · plain data</div><pre><code>{hl_json(HERO_JSON)}</code></pre></div>
  </div>
  <ol class="demo-steps">{steps}</ol>
</div>'''


def hero_lines():
    """Lines fanning in from the top edge and running down as a channel under the signup, with pulses flowing along them."""
    n, W = 16, 1600
    paths, pulses = [], []
    for i in range(n):
        x0 = -260 + i * (W + 520) / (n - 1)
        xe = W / 2 - 112 + i * 15
        d = f"M{x0:.0f} -10 C{x0:.0f} 260 {xe:.0f} 300 {xe:.0f} 560 L{xe:.0f} 1000"
        paths.append(f'<path d="{d}"/>')
        if i % 3 == 1:
            pulses.append(f'<path class="pulse" d="{d}" style="--dl:{(i * 0.53) % 6:.2f}s;--t:{6.2 + (i % 4) * 0.7:.1f}s"/>')
    return (f'<svg class="hero-lines" viewBox="0 0 {W} 1000" preserveAspectRatio="xMidYMin slice" aria-hidden="true">'
            f'<g class="hl-base">{"".join(paths)}</g><g class="hl-pulse">{"".join(pulses)}</g></svg>')


def hero_ribbons():
    """Ribbon-like bundles of lines flowing across the hero (a nod to the ribbons in the NexFlo launch art), with data pulses travelling along them.

    The middle wave (x -60 to 1660) is the original design. EXTRA more waves are added on each side so the
    ribbons reach the edges of very wide screens; the SVG is cropped to the screen width (see .hero-ribbons).
    Longer paths would make one pulse spend most of its time off screen on normal laptops, so each ribbon
    gets several evenly spaced pulses, and the timing is scaled so they move at the original speed."""
    EXTRA, SEG = 2, 860
    x0, x1 = -60 - EXTRA * SEG, 1660 + EXTRA * SEG

    def cubic_len(p0, p1, p2, p3, n=40):
        pts = [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * e
                     for a, b, c, e in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]
        return sum(((x2 - x1_) ** 2 + (y2 - y1) ** 2) ** 0.5 for (x1_, y1), (x2, y2) in zip(pts, pts[1:]))

    def ribbon(yy, amp):
        # Each added segment is one S-shaped wave (dips below the centre line, then rises above it, or the
        # reverse). The left waves end with the tangent the original wave starts with at -60, and the right
        # waves carry on smoothly from where it ends at 1660, so there are no kinks at the joins.
        segs = []
        for i in range(EXTRA):
            end = x0 + (i + 1) * SEG
            segs.append(((end - 300, yy + amp), (end, yy)))
        segs.append(((520, yy + amp), (800, yy)))
        segs.append(((1360, yy - amp), (1660, yy + 10)))
        for i in range(EXTRA):
            end = 1660 + (i + 1) * SEG
            segs.append(((end - 300, yy + 10 - amp), (end, yy + 10)))
        first_c1 = (x0 + 300, yy - amp)
        d = f"M{x0} {yy} C {first_c1[0]} {first_c1[1]} {segs[0][0][0]} {segs[0][0][1]} {segs[0][1][0]} {segs[0][1][1]}"
        length = cubic_len((x0, yy), first_c1, segs[0][0], segs[0][1])
        prev, prev_c2 = segs[0][1], segs[0][0]
        for c2, end in segs[1:]:
            c1 = (2 * prev[0] - prev_c2[0], 2 * prev[1] - prev_c2[1])
            length += cubic_len(prev, c1, c2, end)
            d += f" S {c2[0]} {c2[1]} {end[0]} {end[1]}"
            prev, prev_c2 = end, c2
        return d, length

    bundles = [(470, 1, 5.5), (590, -1, 6.5), (700, 1, 7.5)]
    base, pulses = [], []
    for k, (y, direction, t) in enumerate(bundles):
        amp = 110 - k * 18
        for j in range(3):
            d, length = ribbon(y + j * 10, amp)
            base.append(f'<path d="{d}"/>')
            if j == 1:
                # Originally a 70-unit pulse travelled 2170 units in t seconds. Keep that speed on the longer path.
                n = EXTRA * 2 + 1
                travel = length + 70
                dur = t * travel / 2170
                for p in range(n):
                    pulses.append(f'<path class="{"rev" if direction < 0 else ""}" d="{d}" pathLength="2100" '
                                  f'style="stroke-dasharray:{70 * 2100 / length:.1f} 2100;--t:{dur:.2f}s;--dl:{k * 1.7 - p * dur / n:.2f}s"/>')
    vb_w = x1 - x0 + 40
    return (f'<svg class="hero-ribbons" viewBox="{x0 - 20} 0 {vb_w} 900" preserveAspectRatio="xMidYMin slice" aria-hidden="true">'
            f'<g class="hr-base">{"".join(base)}</g><g class="hr-pulse">{"".join(pulses)}</g></svg>')


# Hero background: "ribbons" (default, flowing ribbon bundles) or "lines" (fanning lines with pulses).
# HERO=lines python3 build.py builds the lines version into dist-lines/.
HERO_STYLE = __import__("os").environ.get("HERO", "ribbons")


def hero_background():
    return hero_ribbons() if HERO_STYLE == "ribbons" else hero_lines()


CLOUD_GLYPH = '<svg class="glyph" viewBox="0 0 240 140" aria-hidden="true"><g fill="currentColor"><rect x="16" y="76" width="208" height="64" rx="32"/><circle cx="72" cy="84" r="46"/><circle cx="128" cy="60" r="58"/><circle cx="184" cy="88" r="40"/></g></svg>'


def orbit_view(vb, orbits, items, core, cls, label, narrow=0.8):
    """Elliptical orbits. Labels travel along the ellipses but stay upright: motion.js moves them with translate only."""
    vw, vh = vb
    import json
    paths = "".join(f'<ellipse cx="{vw / 2}" cy="{vh / 2}" rx="{rx}" ry="{ry}" transform="rotate({tilt} {vw / 2} {vh / 2})"/>' for rx, ry, tilt in orbits)
    spans = []
    for it in items:
        o, phase, speed = it["o"], it["phase"], it["speed"]
        if it.get("dot"):
            spans.append(f'<span class="o-dot{" ok" if it["dot"] == "ok" else ""}" data-o="{o}" data-phase="{phase}" data-speed="{speed}"></span>')
        else:
            inner = (f'<b>{it["code"]}</b>' if it.get("code") else CLOUD_GLYPH if it.get("glyph") else "") + it["text"]
            spans.append(f'<span class="o-item" data-o="{o}" data-phase="{phase}" data-speed="{speed}">{inner}</span>')
    return (f'<div class="orbit-view {cls}" data-orbit data-vb="{vw} {vh}" data-narrow="{narrow}" data-orbits=\'{json.dumps(orbits)}\' '
            f'role="img" aria-label="{label}" style="aspect-ratio:{vw}/{vh}">'
            f'<svg class="o-paths" viewBox="0 0 {vw} {vh}" aria-hidden="true">{paths}</svg>{core}{"".join(spans)}</div>')


def orbit():
    items = [
        dict(o=0, phase=200, speed=4.5, text="Inbound partners", glyph=True),
        dict(o=0, phase=20, speed=4.5, code="EDI", text="X12 / EDIFACT"),
        dict(o=0, phase=110, speed=4.5, text="SFTP", glyph=True),
        dict(o=1, phase=320, speed=-3.6, text="Outbound partners", glyph=True),
        dict(o=1, phase=150, speed=-3.6, code="&lt;/&gt;", text="XML"),
        dict(o=1, phase=60, speed=-3.6, code="{ }", text="JSON"),
        dict(o=2, phase=250, speed=6, text="API", glyph=True),
        dict(o=2, phase=10, speed=6, code="CSV", text="Spreadsheets"),
        dict(o=2, phase=130, speed=6, text="Flat files"),
        dict(o=0, phase=0, speed=16, dot="in"), dict(o=0, phase=180, speed=16, dot="in"),
        dict(o=1, phase=90, speed=-14, dot="ok"), dict(o=2, phase=160, speed=22, dot="ok"),
    ]
    core = ('<div class="o-core"><span class="o-halo"></span><div class="o-plate">'
            '<img src="assets/cloud-icon.png" alt="" width="1106" height="689"></div></div>')
    return orbit_view((1000, 620), [[450, 118, -14], [410, 150, 16], [330, 200, 4]], items, core, "o-home",
                      "Messages in EDI, XML, JSON, CSV and flat files arriving over SFTP or API, translated by TradeFlo and sent on to your partners")


DOCS = [
    ("850", "Purchase order", "A customer's order: what they want, how many, and where to ship it."),
    ("856", "Shipping notice", "What's in each box and pallet, sent before the truck arrives. Late or wrong ones often lead to fines."),
    ("810", "Invoice", "Your bill for the order, matched to what you shipped so you get paid on time."),
    ("997", "Receipt", "An automatic note confirming a file arrived. NexFlo sends and tracks these for you."),
    ("855", "Order confirmation", "Your reply saying you accept the order, or which items you can't fill."),
    ("846", "Inventory update", "How much stock you have, so partners don't order what you can't send."),
    ("ORDERS · INVOIC · DESADV", "International (EDIFACT)", "The same orders, invoices and shipping notices, in the format used outside North America."),
    ("837 · 835 · 270/271", "Healthcare (coming 2027)", "Claims, payments and insurance eligibility checks, handled by CareFlo."),
]

TILE_ICONS = {
    "tradeflo": '<path d="M3 7.5l9-4.5 9 4.5-9 4.5-9-4.5zM3 7.5v9l9 4.5 9-4.5v-9M12 12v9"/>',
    "careflo": '<path d="M9 3h6v3H9zM6 5H4v16h16V5h-2M8 12h8M8 16h5"/>',
    "healthflo": '<path d="M2 12h4l3-8 4 16 3-8h6"/>',
}
TILE_CHIPS = {"tradeflo": ("Orders", "Invoices", "Shipping", "Receipts"), "careflo": ("Claims", "Payments", "Eligibility", "Status"),
              "healthflo": ("Records", "Lab results", "EHR", "Apps")}


def tile_art(p):
    a, b, c, d = TILE_CHIPS[p["key"]]
    items = [dict(o=0, phase=20, speed=5, text=a), dict(o=0, phase=200, speed=5, text=b),
             dict(o=1, phase=110, speed=-4, text=c), dict(o=1, phase=290, speed=-4, text=d),
             dict(o=0, phase=300, speed=14, dot="in"), dict(o=1, phase=30, speed=-12, dot="ok")]
    core = (f'<div class="t-node"><div class="t-cloud"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{TILE_ICONS[p["key"]]}</svg></div></div>')
    return orbit_view((1000, 460), [[400, 120, -8], [300, 150, 10]], items, core,
                      "t-art" + ("" if p["status"] == "live" else " soon"), f'{p["name"]} illustration', narrow=0.9)


def product_tiles():
    out = []
    for p in PRODUCTS:
        live = p["status"] == "live"
        out.append(f'''<a class="tile tile-box" href="{p["href"]}">
  {tile_art(p)}
  <div class="tile-body">
    <div class="tile-head"><h3>{p["name"]}</h3>{status_badge(p["status"])}</div>
    <p class="tile-sub">{p["sub"]}</p>
    <p class="tile-desc">{p["line"]}</p>
    <div class="tile-for"><span>Best for</span>{p["for"][0].upper() + p["for"][1:]}</div>
    <span class="tile-cta">{"Explore " + p["name"] if live else "Learn more"} <i aria-hidden="true">→</i></span>
  </div>
</a>''')
    return f'<div class="tiles">{"".join(out)}</div>'


FLOW_STEPS = [
    ("Connect your systems", "Connect the business software and platforms that need to exchange information."),
    ("Set up your connections", "Configure how information moves between systems."),
    ("Exchange information", "Send and receive business documents through automated workflows."),
    ("Track everything", "Monitor document activity, transaction statuses and potential issues."),
]


def flow_steps():
    items = "".join(f'<li class="f4"><span class="f4-n">{i}</span><div><b>{t}</b><p>{d}</p></div></li>' for i, (t, d) in enumerate(FLOW_STEPS, 1))
    return f'<ol class="flow4 flow4-row" data-cycle>{items}</ol>'


@page("index.html", "NexFlo Cloud | Business data, flowing better",
      "NexFlo Cloud helps businesses connect their software, exchange important documents like orders, invoices and claims, and reduce manual work.")
def home():
    words = "Business Data. Flowing Better.".split()
    title = " ".join(f'<span class="w{" accent" if i > 1 else ""}" style="--i:{i}">{w}</span>' for i, w in enumerate(words))
    chat = f'''<div class="chat" data-chat aria-label="Example support conversation">
  <div class="msg"><span class="avatar them">JM</span><div><b>Jordan, Acme Supply</b><time>9:12 AM</time><p>Walmart rejected this morning's shipping notice. Any idea why?</p></div></div>
  <div class="typing" hidden><i></i><i></i><i></i></div>
  <div class="msg"><span class="avatar">NF</span><div><b>NexFlo team</b><time>9:31 AM</time><p>Walmart needs a label number on every box. We've added it to your setup, so the next one will go through.</p></div></div>
  <p class="chat-note">Example conversation</p>
</div>'''
    row = lambda c, n, d: f'<div class="doc"><h3><code>{c}</code><span>{n}</span></h3><p>{d}</p></div>'
    docs_main = "".join(row(*x) for x in DOCS[:4])
    docs_more = "".join(row(*x) for x in DOCS[4:])
    return f'''
<section class="hero-s">
  {hero_background()}
  <div class="container">
    <h1>{title}</h1>
    <p class="sub">NexFlo Cloud helps businesses connect their software, exchange important documents, and reduce manual work.</p>
    {signup_inline("home-hero", button="Join early access")}
    <p class="hero-note">New to EDI? It's the standard way companies send orders, invoices and claims to each other. NexFlo handles it for you. <a href="what-is-edi.html">Learn more</a></p>
    <div class="hero-stage"><div class="arc hero-circle"></div>{hero_demo()}</div>
  </div>
  <div class="hero-strip"><div class="container"><p>TradeFlo early access is open · CareFlo and HealthFlo are coming in 2027</p></div>{ticker()}</div>
</section>

<section class="s-light sec-tight" id="products"><div class="container">
  <div class="section-head"><span class="label">Products</span><h2>Three products for three kinds of businesses</h2>
    <p class="lead">Pick the one that matches what you do. All three are in development and run on the same NexFlo platform.</p></div>
  {product_tiles()}
</div></section>

<section class="sec-tight" id="how-it-works"><div class="container">
  <div class="how-head"><div><span class="label">How it works</span><h2>Set it up once. Then it runs on its own.</h2></div>
    <p>No retyping orders from emails or portals. Once your systems and partners are connected, documents move back and forth automatically.</p></div>
  {flow_steps()}
  <p class="flow4-note">This is how the NexFlo platform is being built to work. It's in development and not live yet.</p>
</div></section>

<section class="sec-tight"><div class="container frows">
  <div class="frow">
    <div class="frow-text"><span class="label">Works with what you have</span><h2>Use a spreadsheet, or connect your software</h2>
      <p>No tech team? Save a spreadsheet into a secure shared folder and NexFlo turns it into the format your partner needs. Have developers? They can connect your systems directly.</p>
      <details class="more"><summary>The technical details</summary><p>The shared folder uses SFTP, a secure way for companies to swap files. The API accepts and returns JSON, the format most modern software uses. The API is in development and may change before launch.</p></details></div>
    <div class="vis"><div class="arc" data-arc="0.6"></div>{win_tabs([("Shared folder", "", hl_shell(SFTP_SESSION)), ("API", "", hl_js(API_JS))], "Illustration")}</div>
  </div>
  <div class="frow flip">
    <div class="frow-text"><span class="label">One dashboard</span><h2>See every order and invoice in one place</h2>
      <p>Know what arrived, what was sent and what needs attention, before a small mistake turns into a fine from your retailer.</p>
      <p class="small">Illustration of the planned dashboard with sample data. Not a live product screenshot.</p></div>
    <div class="vis tall"><div class="arc" data-arc="0.6"></div>{dashboard_mock()}</div>
  </div>
</div></section>

<section class="orbit-sec sec-tight"><div class="container orbit-split">
  {orbit()}
  <div class="frow-text"><span class="label">Translation engine</span><h2>Any format in. The right format out.</h2>
    <p>Your partners send EDI (X12 or EDIFACT), XML, JSON, CSV or flat files, over SFTP or an API. TradeFlo is being built to check each message, translate it into the format the other side needs, and send it on.</p>
    <p>Each partner's rules live in one place, so adding a new one doesn't mean starting over.</p>
    <a class="btn btn-primary mt-2" href="tradeflo.html">Explore TradeFlo</a></div>
</div></section>

<section class="sec-tight"><div class="container doc-split">
  <div class="doc-head"><h2>The documents your partners will ask for</h2>
    <p class="lead">In EDI, every type of document has a number. Here's what the common ones mean.</p>
    <a class="link-arrow" href="retail-edi-documents.html">Read the full guide</a></div>
  <div class="doclist">{docs_main}<details class="doc-more"><summary>Show 4 more</summary>{docs_more}</details></div>
</div></section>

<section class="s-light sec-tight"><div class="container split">
  <div class="frow-text"><span class="label">Support</span><h2>Real people, quick answers</h2>
    <p>Email the NexFlo team and get a reply within one business day, plus hands-on help connecting your first trading partner.</p>
    <a class="link-arrow" href="contact.html">Contact us</a></div>
  <div class="vis vis-blue"><div class="arc" data-arc="0.6"></div>{chat}</div>
</div></section>

<section class="s-accent sec-tight"><div class="container">
  <div class="section-head center"><span class="label">Security</span><h2>Built carefully, claimed honestly</h2></div>
  <div class="scards">
    <div class="scard"><h3>Your data is encrypted</h3><p>Planned from day one: encryption for every connection and every stored document.</p></div>
    <div class="scard"><h3>Only the right people get in</h3><p>Planned for every account: individual logins, two-step sign-in and permissions.</p></div>
    <div class="scard"><h3>Ready for healthcare rules</h3><p>For healthcare customers, we're prepared to sign a Business Associate Agreement (BAA) where required.</p></div>
    <div class="scard"><h3>No claims we can't back up</h3><p>We don't claim HIPAA certification or a SOC 2 report today. They'll be on our <a href="security.html" style="text-decoration:underline">Security page</a> once independently verified.</p></div>
  </div>
</div></section>

<section class="cta-s">
  <div class="arc cta-circle" data-arc="0.8"></div>
  <div class="container cta-in">
    <h2>Ready to simplify your integrations?</h2>
    <p>Join early access, or tell us about your partners and documents. No technical knowledge needed.</p>
    <div class="row"><a class="btn btn-ghost arrow" href="demo.html">Talk to NexFlo</a><a class="btn btn-white btn-lg" href="early-access.html">Join early access</a></div>
  </div>
</section>
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


# ---------------------------------------------------------------- TradeFlo: how it works diagram
TF_FORMATS = [  # key, tag, name, detail
    ("edi", "EDI", "EDI", "X12 · EDIFACT"),
    ("xml", "&lt;/&gt;", "XML", "Any schema"),
    ("json", "{ }", "JSON", "Clean, documented"),
    ("csv", "CSV", "CSV", "Spreadsheet rows"),
    ("flat", "TXT", "Flat files", "Delimited · fixed width"),
]
TF_CONNS = [("folder", "SFTP", "Secure file transfer"), ("plug", "API", "REST or SOAP")]
# Examples the diagram cycles through: from format, to format, connection in, connection out, caption.
TF_EXAMPLES = [
    ("edi", "json", 0, 1, "A purchase order arrives as EDI. Your system gets clean JSON."),
    ("csv", "edi", 1, 0, "Your invoice leaves as a spreadsheet. Your partner gets EDI."),
    ("xml", "edi", 1, 0, "Your warehouse sends a shipping notice in XML. It goes out as EDI."),
    ("edi", "flat", 0, 0, "An inventory request arrives as EDI. Your older system gets a flat file."),
    ("json", "edi", 1, 1, "Your store confirms an order in JSON. Your partner gets EDI."),
]
TF_FEATURES = [
    ("swap", "Many formats", "EDI, XML, JSON, CSV and flat files, in and out."),
    ("users", "Partner setup", "Each partner's IDs and connection details in one place."),
    ("shield", "Secure exchange", "SFTP and encrypted API connections, with a record of every file."),
    ("sliders", "Flexible mapping", "Reshape, check and fill in fields to match each partner."),
    ("cloud", "Runs in the cloud", "Nothing to install or keep running on your side."),
]


def tradeflo_flow():
    """Partners -> TradeFlo (formats in, translate, formats out) -> your systems or partners.
    motion.js (data-tf) steps through TF_EXAMPLES, lighting up the matching connection and formats."""
    import json
    conns = lambda: "".join(f'<li class="tf-conn">{icon(i, "tf-ico")}<span><b>{n}</b><small>{d}</small></span></li>' for i, n, d in TF_CONNS)
    fmts = lambda: "".join(f'<li data-k="{k}"><span class="tf-tag">{t}</span><span><b>{n}</b><small>{d}</small></span></li>' for k, t, n, d in TF_FORMATS)
    wire = '<div class="tf-wire" aria-hidden="true"><span class="tf-line"></span><i></i><i></i><i></i></div>'
    feats = "".join(f'<li>{icon(i, "tf-fico")}<b>{t}</b><span>{d}</span></li>' for i, t, d in TF_FEATURES)
    ex = json.dumps([list(e) for e in TF_EXAMPLES]).replace("'", "&#39;")
    first = TF_EXAMPLES[0]
    return f'''
<section class="s-light tf-sec"><div class="container">
  <div class="section-head center"><span class="eyebrow">How it works</span><h2>Every document, in the format each side needs</h2>
    <p class="lead">TradeFlo picks up documents from your partners, translates them, and hands them to your systems, or sends your replies back in the format each partner expects.</p></div>
  <div class="tf" data-tf data-ex='{ex}'>
    <div class="tf-side tf-in"><h3>From your partners</h3><ul>{conns()}</ul></div>
    {wire}
    <div class="tf-engine">
      <div class="tf-cloud" aria-hidden="true"></div>
      <div class="tf-head"><b>Trade<span>Flo</span></b><small>Translation engine</small></div>
      <div class="tf-grid">
        <div class="tf-list tf-from"><p class="tf-cap">Comes in as</p><ul>{fmts()}</ul></div>
        <div class="tf-core"><div class="tf-disc"><span class="tf-ring"></span>{icon("swap", "tf-cico")}</div>
          <span class="tf-pair"><b data-a>EDI</b><i>→</i><b data-b>JSON</b></span></div>
        <div class="tf-list tf-to"><p class="tf-cap">Goes out as</p><ul>{fmts()}</ul></div>
      </div>
      <p class="tf-say" aria-live="polite">{first[4]}</p>
    </div>
    {wire}
    <div class="tf-side tf-out"><h3>To your systems or partners</h3><ul>{conns()}</ul></div>
  </div>
  <ul class="tf-feats">{feats}</ul>
  <p class="tf-note">Illustration of how TradeFlo is designed to work. TradeFlo is in development.</p>
</div></section>'''


def product_page(name, mark, status, lead, who, example_intro, demo, features, standards_label, standards, cta, notice="", product="", flow=""):
    badge = status_badge(status)
    is_live = status == "live"
    actions = (f'<a class="btn btn-primary btn-lg" href="early-access.html?product={name}">Join early access</a>'
               f'<a class="btn btn-secondary btn-lg" href="pricing.html?product={name}#quote">Request pricing</a>') if is_live else (
               f'<a class="btn btn-primary btn-lg" href="#waitlist">Join the waitlist</a>')
    feat_html = "".join(f'<div class="feature">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in features)
    who_html = "".join(f"<li>{w}</li>" for w in who)
    std_html = "".join(f'<span class="doc-chip" title="{d}">{c}</span>' for c, d in standards)
    std_rows = "".join(f'<tr><td><span class="doc-chip">{c}</span></td><td>{d}</td></tr>' for c, d in standards)
    title_html = f'{mark}<span style="color:var(--blue)">Flo</span>'
    cta_html = cta_band(*cta, product=name, secondary=is_live)
    sub = next(p["sub"] for p in PRODUCTS if p["name"] == name)
    return page_hero(title_html, lead, sub, [("Products", "products.html"), (name, None)], actions, badge) + f'''
<section><div class="container split top">
  <div><span class="eyebrow">What it does</span><h2>{example_intro[0]}</h2><p class="lead">{example_intro[1]}</p>{notice}</div>
  <div class="card"><h3>Who it's for</h3><ul class="checks mt-2">{who_html}</ul></div>
</div></section>{flow}
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


@page("tradeflo.html", "TradeFlo | EDI for suppliers and manufacturers",
      "TradeFlo translates X12 and EDIFACT documents like 850, 810 and 856 into clean JSON, with SFTP, API and transaction tracking.", "products")
def tradeflo():
    return product_page(
        "TradeFlo", "Trade", "live",
        "Make it easier to send and receive purchase orders, invoices, and shipping information between your business and its partners. TradeFlo is in development, with early access open now.",
        ["Manufacturers selling to big-box retailers", "Distributors and wholesalers with many trading partners",
         "Retail and e-commerce suppliers facing new EDI requirements", "Teams outgrowing expensive legacy EDI providers"],
        ("Your partners' documents, in a format your systems understand",
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
        flow=tradeflo_flow(),
    )


@page("careflo.html", "CareFlo | Healthcare claims and eligibility translation",
      "CareFlo is a planned HIPAA X12 translation layer for claims, eligibility, claim status and remittance. Coming 2027.", "products")
def careflo():
    notice = ('<div class="notice mt-3"><div><strong>Integration and translation come first.</strong> CareFlo is the layer that '
              'translates and validates your HIPAA X12 transactions. Payer connectivity is arranged separately, through your '
              'existing clearinghouse or a partner we help you set up.</div></div>')
    return product_page(
        "CareFlo", "Care", "soon",
        "Simplify how healthcare businesses exchange claims, billing information, and insurance-related documents. CareFlo is in development and planned for 2027.",
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


@page("healthflo.html", "HealthFlo | HL7 and FHIR data exchange",
      "HealthFlo is a planned HL7 v2 and FHIR integration product for health tech and hospital systems. Coming 2027.", "products")
def healthflo():
    return product_page(
        "HealthFlo", "Health", "soon",
        "Help healthcare software and medical systems exchange important information more easily. HealthFlo is in development and planned for 2027.",
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
    ("How will pricing work?", "In packages. Each product will have monthly Starter, Growth and Enterprise packages, and each package includes a fixed number of documents or transactions per month. We're finalizing the exact prices and allowances."),
    ("Is it pay-as-you-go?", "No. You'll pick a monthly package with a set allowance, so your monthly cost is predictable."),
    ("Why aren't prices listed yet?", "We're still setting final prices. We'd rather publish numbers we can stand behind than change them later."),
    ("Are there setup fees or long contracts?", "Those details aren't decided yet. Whatever they are, you'll have them in writing before you sign anything."),
    ("Do founding customers lock in launch pricing?", "Yes. Founding customers keep their launch pricing as the product grows."),
]


PACKAGES = {
    "TradeFlo": ("documents", [("Starter", "For small businesses getting started with EDI."),
                               ("Growth", "For growing businesses trading with more partners."),
                               ("Enterprise", "For established businesses with higher volumes and more complex needs.")]),
    "CareFlo": ("transactions", [("Starter", "For smaller practices and billing teams."),
                                 ("Growth", "For growing healthcare organizations and billing companies."),
                                 ("Enterprise", "For organizations with high volumes and complex needs.")]),
    "HealthFlo": ("transactions", [("Starter", "For teams making their first system connections."),
                                   ("Growth", "For growing health tech teams with more connections."),
                                   ("Enterprise", "For hospitals and vendors with complex integration needs.")]),
}


@page("pricing.html", "Pricing", "NexFlo Cloud pricing: monthly Starter, Growth and Enterprise packages for TradeFlo, CareFlo and HealthFlo, each with a fixed monthly allowance.", "pricing")
def pricing():
    tabs = "".join(f'<button class="ptab" role="tab" aria-selected="{str(i == 0).lower()}" aria-controls="pp-{p["key"]}" id="pt-{p["key"]}">{p["name"]}</button>'
                   for i, p in enumerate(PRODUCTS))
    panels = []
    for i, p in enumerate(PRODUCTS):
        unit, tiers = PACKAGES[p["name"]]
        live = p["status"] == "live"
        cards = []
        for tier, desc in tiers:
            if tier == "Enterprise":
                btn = '<a class="btn btn-secondary" href="contact.html">Contact sales</a>'
            elif live:
                btn = f'<a class="btn {"btn-primary" if tier == "Growth" else "btn-secondary"}" href="?product={p["name"]}#quote">Request pricing</a>'
            else:
                btn = f'<a class="btn {"btn-primary" if tier == "Growth" else "btn-secondary"}" href="early-access.html?product={p["name"]}">Join early access</a>'
            cards.append(f'''<div class="price-card{" featured" if tier == "Growth" else ""}">
  <h3>{tier}</h3><p class="muted">{desc}</p>
  <div class="price">Pricing coming soon</div>
  <ul class="checks"><li>A fixed number of {unit} each month</li><li>Allowance to be announced</li></ul>
  {btn}</div>''')
        panels.append(f'''<div class="ppanel" role="tabpanel" id="pp-{p["key"]}" aria-labelledby="pt-{p["key"]}"{"" if i == 0 else " hidden"}>
  <div class="ppanel-head"><p><b>{p["name"]}</b> · {p["sub"]} {status_badge(p["status"])}</p></div>
  <div class="grid grid-3">{"".join(cards)}</div></div>''')
    how = [("Choose your product", "TradeFlo, CareFlo or HealthFlo, depending on what your business does."),
           ("Pick a package", "Starter, Growth or Enterprise, based on how much you send and receive."),
           ("Get a fixed monthly allowance", "Each package includes a set number of documents or transactions every month.")]
    how_html = "".join(f'<li><span>{i}</span><div><b>{t}</b><p>{d}</p></div></li>' for i, (t, d) in enumerate(how, 1))
    return page_hero("Simple monthly packages",
                     "Each NexFlo product comes in three monthly packages. Every package includes a fixed number of documents or transactions per month, so you know what to expect. Final prices are being set now.",
                     "Pricing", [("Home", "index.html"), ("Pricing", None)]) + f'''
<section class="sec-tight"><div class="container">
  <ol class="pkg-how">{how_html}</ol>
  <div class="pricing-tabs" data-tabs>
    <div class="ptabs" role="tablist" aria-label="Choose a product">{tabs}</div>
    {"".join(panels)}
  </div>
  <p class="small muted mt-3">Prices and monthly allowances haven't been finalized. We'll publish them here once they're confirmed.</p>
</div></section>

<section class="section-soft sec-tight" id="quote"><div class="container split top">
  <div><span class="eyebrow">Request pricing</span><h2>Tell us what you need</h2>
    <p class="lead">Roughly how many orders, invoices or claims do you handle each month? We'll reply from {SALES} within one business day.</p>
    <ul class="checks mt-4"><li>No obligation</li><li>Founding customers lock in launch pricing</li><li>A real person replies, not an automated sequence</li></ul></div>
  <form class="form-card" data-form="Pricing request" data-to="{SALES}" novalidate>
    {HONEYPOT}
    <div class="form-body"><div class="form-grid">
      <div class="field"><label for="q-name">Name</label><input id="q-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="q-email">Work email</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field"><label for="q-company">Company</label><input id="q-company" name="company" required autocomplete="organization"></div>
      <div class="field"><label for="q-product">Product of interest</label><select id="q-product" name="product" required>{opt(PRODUCT_OPTS)}</select></div>
      <div class="field"><label for="q-volume">Orders, invoices or claims per month</label><select id="q-volume" name="monthly_volume" required>{opt(VOLUME_OPTS)}</select></div>
      <div class="field"><label for="q-provider">Current EDI provider <span class="opt">(if any)</span></label><input id="q-provider" name="current_provider" placeholder="e.g. none yet"></div>
      <div class="field full"><label for="q-notes">Anything else? <span class="opt">(optional)</span></label><textarea id="q-notes" name="notes" placeholder="Who you trade with, the software you use, timelines…"></textarea></div>
    </div>
    <div class="form-foot"><small>By submitting you agree to our <a href="privacy.html">Privacy Policy</a>.</small><button class="btn btn-primary" type="submit">Request pricing</button></div></div>
    {form_success("Thanks, we've got it.", f"We'll get back to you from {SALES} within one business day.")}
  </form>
</div></section>

<section class="sec-tight"><div class="container narrow">
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
    ("Where are you based?", "Minnesota. NexFlo is a small team, so you talk directly to the people building it."),
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


@page("about.html", "About", "NexFlo Cloud is a Minnesota company building affordable, enterprise-grade integration for growing businesses.", "company")
def about():
    return page_hero("EDI for the suppliers big providers overlook",
                     "NexFlo Cloud exists to make EDI and data integration affordable and simple for the businesses that big providers overlook.",
                     "About us", [("Company", None), ("About", None)]) + f'''
<section><div class="container split top">
  <div><span class="eyebrow">Our mission</span><h2>Less friction. More flow.</h2>
    <p class="lead">Growing businesses shouldn't have to choose between expensive legacy EDI providers and doing everything by hand. We're building the middle path: modern, transparent and easy to start.</p></div>
  <div><span class="eyebrow">Why NexFlo exists</span>
    <p>Small manufacturers and suppliers pay enterprise prices for EDI they barely understand, then wait days for help when something breaks.</p>
    <p class="mb-0">NexFlo fixes that. TradeFlo comes first, for suppliers trading with retailers. CareFlo and HealthFlo bring the same approach to healthcare data in 2027.</p></div>
</div>
<div class="container grid grid-3 mt-6">
  <div class="card">{icon("map")}<h3 class="mt-2">Based in Minnesota</h3><p>Built in the Midwest, for businesses everywhere.</p></div>
  <div class="card">{icon("tag")}<h3 class="mt-2">Transparent by default</h3><p>Clear pricing and honest claims about what's built and what's planned.</p></div>
  <div class="card">{icon("chat")}<h3 class="mt-2">Direct support</h3><p>No ticket queues. You talk to the person who wrote the code.</p></div>
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
      <div class="field"><label for="c-company">Company <span class="opt">(optional)</span></label><input id="c-company" name="company" autocomplete="organization"></div>
      <div class="field"><label for="c-phone">Phone <span class="opt">(optional)</span></label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
      <div class="field"><label for="c-product">Product of interest <span class="opt">(optional)</span></label><select id="c-product" name="product">{opt(PRODUCT_OPTS)}</select></div>
      <div class="field"><label for="c-volume">Orders, invoices or claims per month <span class="opt">(optional)</span></label><select id="c-volume" name="monthly_volume">{opt(VOLUME_OPTS)}</select></div>
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


@page("demo.html", "Talk to us", "Request a consultation with NexFlo Cloud about your trading partners, documents and how NexFlo could fit.")
def demo():
    return page_hero("Talk to us", "Tell us who you trade with and what's slowing you down. We'll set up a call and explain plainly how NexFlo can help. No technical knowledge needed.",
                     "Request a consultation", [("Home", "index.html"), ("Talk to us", None)]) + f'''
<section><div class="container split top">
  <form class="form-card" data-form="Consultation request" data-to="{SALES}">
    {HONEYPOT}
    <div class="form-body"><div class="form-grid">
      <div class="field"><label for="d-name">Name</label><input id="d-name" name="name" required autocomplete="name"></div>
      <div class="field"><label for="d-email">Work email</label><input id="d-email" name="email" type="email" required autocomplete="email"></div>
      <div class="field"><label for="d-company">Company</label><input id="d-company" name="company" required autocomplete="organization"></div>
      <div class="field"><label for="d-product">Product of interest</label><select id="d-product" name="product" required>{opt(PRODUCT_OPTS)}</select></div>
      <div class="field"><label for="d-volume">Orders, invoices or claims per month</label><select id="d-volume" name="monthly_volume">{opt(VOLUME_OPTS)}</select></div>
      <div class="field"><label for="d-contact">Best way to reach you</label><select id="d-contact" name="preferred_contact">{opt(["Email", "Phone call", "Video call"])}</select></div>
      <div class="field full"><label for="d-msg">What's the challenge? <span class="opt">(optional)</span></label><textarea id="d-msg" name="message" placeholder="e.g. Walmart asked us to start using EDI, or our current provider is too expensive"></textarea></div>
    </div>
    <div class="form-foot"><small>By submitting you agree to our <a href="privacy.html">Privacy Policy</a>.</small><button class="btn btn-primary" type="submit">Request a consultation</button></div></div>
    {form_success("Request received.", "We'll email you within one business day to find a time.")}
  </form>
  <div><h2>What we'll talk about</h2>
    <ul class="checks mt-3"><li>Who you trade with and which documents they ask for</li><li>How you handle orders and invoices today</li>
      <li>How NexFlo would fit, step by step</li><li>Early-access timing and pricing as it's set</li></ul>
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
      <li>A direct line to the NexFlo team</li><li>A real say in what we build next</li></ul>
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



LOGO_IMG = '<img src="assets/logo.png" alt="NexFlo Cloud" width="154" height="46">'
LOGO_PAIR = '<img src="assets/logo-dark.png" alt="NexFlo Cloud" width="154" height="46">'


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    # Fingerprint CSS/JS URLs so browsers fetch the new file whenever it changes, instead of a cached old one.
    import hashlib
    stamps = {name: hashlib.md5((ROOT / "assets" / name).read_bytes()).hexdigest()[:10] for name in ("styles.css", "main.js", "motion.js")}
    bare = {"portal.html"}
    for slug, (title, desc, active, fn) in PAGES.items():
        out = layout(title, desc, fn(), active, slug, bare=slug in bare)
        for name, h in stamps.items():
            out = out.replace(f'assets/{name}"', f'assets/{name}?v={h}"')
        out = out.replace(LOGO_IMG, LOGO_PAIR)
        if CLEAN_URLS:
            out = clean_links(out)
        (DIST / slug).write_text(out, encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE_URL}/{'' if s == 'index.html' else s.removesuffix('.html')}</loc></url>" for s in PAGES if s not in ("404.html", "portal.html"))
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages into {DIST}")


if __name__ == "__main__":
    build()
