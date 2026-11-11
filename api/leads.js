// GET /api/leads?key=LEADS_ADMIN_KEY[&format=csv] — owner-only view of captured leads, newest first.
import { list, get } from '@vercel/blob';

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const csvCell = (s) => { s = String(s ?? ''); if (/^[=+\-@]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; };
const COLS = ['received', 'plan', 'email', 'name', 'url', 'category', 'description', 'country', 'page', 'ref'];

export default async function handler(req, res) {
  const key = process.env.LEADS_ADMIN_KEY;
  if (!key || req.query.key !== key) return res.status(404).send('Not found');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex');
  const blobs = [];
  let cursor;
  do { const r = await list({ prefix: 'leads/', cursor, limit: 1000 }); blobs.push(...r.blobs); cursor = r.hasMore ? r.cursor : undefined; } while (cursor);
  const leads = (await Promise.all(blobs.map(async (b) => {
    try { const g = await get(b.pathname, { access: 'private' }); return g ? JSON.parse(await new Response(g.stream).text()) : null; }
    catch { return null; }
  }))).filter(Boolean).sort((a, b) => (a.received < b.received ? 1 : -1));
  if (req.query.format === 'csv') {
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    return res.status(200).send([COLS.join(','), ...leads.map((l) => COLS.map((c) => csvCell(l[c])).join(','))].join('\n'));
  }
  if (req.query.format === 'json') return res.status(200).json(leads);
  const rows = leads.map((l) => `<tr>${COLS.slice(0, 8).map((c) => `<td>${c === 'email' ? `<a href="mailto:${esc(l.email)}">${esc(l.email)}</a>` : esc(l[c])}</td>`).join('')}</tr>`).join('');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(200).send(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AgentIndexed leads</title>
<style>body{font:14px system-ui,sans-serif;margin:16px;background:#0b0b0b;color:#eee}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #333;padding:6px 8px;text-align:left;vertical-align:top}th{color:#86efac}a{color:#86efac}.w{overflow-x:auto}</style>
<h1>AgentIndexed leads (${leads.length})</h1><p>Paid plans = clicked through to Stripe; check Stripe to see if they paid. <a href="?key=${encodeURIComponent(req.query.key)}&format=csv">Download CSV</a></p>
<div class="w"><table><tr>${COLS.slice(0, 8).map((c) => `<th>${c}</th>`).join('')}</tr>${rows || '<tr><td colspan="8">No leads yet.</td></tr>'}</table></div>`);
}
