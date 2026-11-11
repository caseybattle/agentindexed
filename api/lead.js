// POST /api/lead — saves one lead (submit form or "Continue to secure payment" click) to the
// private Vercel Blob store connected to this project (BLOB_READ_WRITE_TOKEN). Called by the
// submit page BEFORE the visitor is sent to Stripe, so abandoned checkouts still leave an email.
import { put } from '@vercel/blob';

const PLANS = new Set(['free', 'featured', 'pro', 'sponsor']);
const clip = (v, n = 500) => String(v ?? '').trim().slice(0, n);

export default async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false }); }
  let d = req.body;
  if (typeof d === 'string') { try { d = JSON.parse(d); } catch { d = {}; } }
  d = d && typeof d === 'object' ? d : {};
  if (clip(d.company_website)) return res.status(200).json({ ok: true });          // honeypot: bots fill hidden field
  const email = clip(d.email, 254);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return res.status(400).json({ ok: false, error: 'email' });
  const lead = {
    received: new Date().toISOString(),
    plan: PLANS.has(d.plan) ? d.plan : 'unknown',
    email,
    name: clip(d.name, 120), url: clip(d.url, 300), category: clip(d.category, 80),
    description: clip(d.description, 300), page: clip(d.page, 200), ref: clip(d.ref, 60),
    country: clip(req.headers['x-vercel-ip-country'], 4),
  };
  try {
    await put(`leads/${lead.received.replace(/[:.]/g, '-')}-${lead.plan}.json`, JSON.stringify(lead),
      { access: 'private', contentType: 'application/json', addRandomSuffix: true });
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('lead save failed', err);
    return res.status(500).json({ ok: false });
  }
}
