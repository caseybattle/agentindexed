/**
 * AgentIndexed lead capture — Google Apps Script web app.
 * Every Submit (free) and every Featured/Pro/Sponsor "Continue to secure payment" click on
 * agentindexed.com POSTs here BEFORE the visitor reaches Stripe. Each one becomes a row in the
 * "Leads" tab of the spreadsheet this script is attached to, and you get an email alert.
 *
 * Setup (about 3 minutes, once):
 *  1. Create a Google Sheet named "AgentIndexed Leads" (sheets.new).
 *  2. Extensions → Apps Script. Delete what's there, paste this whole file, click Save.
 *  3. Deploy → New deployment → type "Web app".
 *       Execute as: Me    Who has access: Anyone
 *     Click Deploy, approve the Google permission prompts, copy the "Web app URL" (ends in /exec).
 *  4. In Vercel → agentindexed → Settings → Environment Variables add LEADS_URL = that URL
 *     (Production + Preview), then redeploy. (Or give the URL to Claude to set.)
 */
var ALERT_EMAIL = 'casbattle19@gmail.com';
var SHEET_NAME = 'Leads';
var HEADERS = ['Received (UTC)', 'Plan', 'Email', 'Agent name', 'Website', 'Category', 'Description', 'Page', 'Ref', 'Status'];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var d = {};
    try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { d = {}; }
    var clip = function (v, n) { return String(v == null ? '' : v).slice(0, n || 500); };
    var email = clip(d.email, 254);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return out_('ignored');   // drop junk/bot posts
    var plan = ['free', 'featured', 'pro', 'sponsor'].indexOf(d.plan) >= 0 ? d.plan : 'unknown';
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sh.getLastRow() === 0) { sh.appendRow(HEADERS); sh.setFrozenRows(1); }
    var row = [new Date().toISOString(), plan, email, clip(d.name, 120), clip(d.url, 300), clip(d.category, 80),
               clip(d.description, 300), clip(d.page, 200), clip(d.ref, 60), plan === 'free' ? 'new submission' : 'sent to Stripe — check if paid'];
    // Stop spreadsheet formula injection from user-typed text.
    row = row.map(function (c) { return /^[=+\-@]/.test(c) ? "'" + c : c; });
    sh.appendRow(row);
    var paid = plan !== 'free';
    MailApp.sendEmail({
      to: ALERT_EMAIL,
      replyTo: email,
      subject: '[AgentIndexed] ' + (paid ? 'Checkout started (' + plan + ')' : 'New free submission') + ': ' + row[3],
      body: [paid ? 'Someone clicked through to Stripe. If no payment shows up in Stripe within a day, follow up — reply to this email to reach them.' : 'New free listing submission.',
             '', 'Plan: ' + plan, 'Email: ' + email, 'Agent: ' + row[3], 'Website: ' + row[4], 'Category: ' + row[5],
             'Description: ' + row[6], '', 'Sheet: ' + ss.getUrl()].join('\n')
    });
    return out_('ok');
  } finally {
    lock.releaseLock();
  }
}

// Visiting the URL in a browser should show "AgentIndexed leads endpoint is live".
function doGet() { return out_('AgentIndexed leads endpoint is live'); }

function out_(s) { return ContentService.createTextOutput(s).setMimeType(ContentService.MimeType.TEXT); }
