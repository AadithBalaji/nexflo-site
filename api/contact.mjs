/*
 * Receives the website's forms (assets/main.js) and emails them to the NexFlo team through Resend.
 *
 * Needs RESEND_API_KEY in Vercel. The sender address must be on a domain verified in Resend;
 * set FORM_FROM in Vercel to use a different sender.
 */
const TEAM = "sales@nexflo.cloud";

// Who receives each form. The browser never picks the recipient, so nobody can use this to email anyone else.
const RECIPIENTS = {
  "Early access": TEAM,
  "Pricing request": TEAM,
  "Consultation request": TEAM,
  // The "Book Demo" email boxes (hero, closing bands): just an email, sent before the visitor sees the full form.
  "Demo request": TEAM,
  Contact: TEAM,
};

// The fields we accept, in the order they appear in the email. Anything else is dropped.
const LABELS = {
  name: "Name",
  email: "Email",
  company: "Company",
  phone: "Phone",
  product: "Product",
  monthly_volume: "Monthly volume",
  current_provider: "Current provider",
  trading_partners: "Trading partners",
  preferred_contact: "Preferred contact",
  message: "Message",
  notes: "Notes",
  source: "Signed up from",
};

const FROM = () => process.env.FORM_FROM || "NexFlo Website <website@nexflo.cloud>";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const MAX_BODY = 20000;
const MAX_FIELD = 5000;
const MAX_PER_MINUTE = 5;

const reply = (body, status) => Response.json(body, { status });
const text = (value) => String(value ?? "").trim().slice(0, MAX_FIELD);
const oneLine = (value) => text(value).replace(/\s+/g, " ").slice(0, 200);

function sameSite(request) {
  try {
    const host = request.headers.get("x-forwarded-host") || request.headers.get("host");
    return new URL(request.headers.get("origin")).host === host;
  } catch {
    return false;
  }
}

// A simple brake on repeat submissions. It's per server instance, so it slows abuse rather than stopping it.
const recent = new Map();
function tooMany(ip) {
  const now = Date.now();
  const hits = (recent.get(ip) || []).filter((t) => now - t < 60000);
  hits.push(now);
  if (recent.size > 5000) recent.clear();
  recent.set(ip, hits);
  return hits.length > MAX_PER_MINUTE;
}

function compose(form, fields, page) {
  const who = oneLine(fields.name) || oneLine(fields.email);
  const company = oneLine(fields.company);
  const lines = Object.keys(LABELS)
    .filter((key) => text(fields[key]))
    .map((key) => `${LABELS[key]}: ${text(fields[key])}`);
  lines.push("", `Sent from: ${oneLine(page) || "unknown page"}`);
  return {
    subject: `${form} from ${who}${company ? ` (${company})` : ""}`,
    body: lines.join("\n"),
  };
}

export async function POST(request) {
  if (!sameSite(request)) return reply({ error: "Not allowed." }, 403);

  const ip = (request.headers.get("x-forwarded-for") || "").split(",")[0].trim() || "unknown";
  if (tooMany(ip)) return reply({ error: "Too many requests." }, 429);

  const raw = await request.text();
  if (raw.length > MAX_BODY) return reply({ error: "Too large." }, 413);

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    return reply({ error: "Invalid request." }, 400);
  }

  const fields = payload && typeof payload.fields === "object" && payload.fields ? payload.fields : {};
  const form = typeof payload?.form === "string" ? payload.form : "";
  if (!Object.hasOwn(RECIPIENTS, form)) return reply({ error: "Unknown form." }, 400);

  // The hidden bot-trap box ("nf_trap"; "website" on pages cached from before) is only filled in by bots.
  // Pretend it worked and send nothing.
  if (text(fields.nf_trap) || text(fields.website)) return reply({ ok: true }, 200);

  const email = oneLine(fields.email);
  if (!EMAIL_RE.test(email)) return reply({ error: "A valid email is required." }, 400);

  const key = process.env.RESEND_API_KEY;
  if (!key) {
    console.error("contact: RESEND_API_KEY is not set");
    return reply({ error: "Email isn't set up yet." }, 503);
  }

  const { subject, body } = compose(form, fields, payload.page);
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: FROM(), to: [RECIPIENTS[form]], reply_to: email, subject, text: body }),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) {
      console.error("contact: Resend returned", res.status, await res.text());
      return reply({ error: "Couldn't send." }, 502);
    }
  } catch (err) {
    console.error("contact: request to Resend failed", err?.name);
    return reply({ error: "Couldn't send." }, 502);
  }
  return reply({ ok: true }, 200);
}
