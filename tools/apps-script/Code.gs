/**
 * VIBE Real Estate — lead capture (Google Sheets + email notification).
 *
 * Setup (once):
 *  1. Create a new Google Sheet, then Extensions → Apps Script, and paste this file.
 *  2. Run `setup` once (it writes the header row, the Status dropdown and the formats).
 *  3. Deploy → New deployment → Web app → Execute as: Me, Who has access: Anyone.
 *  4. Copy the web-app URL into SITE["endpoint"] in tools/site_data.py and run tools/build.py.
 */
var SHEET_NAME = 'Leads';
var EMAIL_TO = 'M.a.fattah79@gmail.com';
var EMAIL_CC = 'Info@mohabdo.com';
var STATUSES = ['New', 'Qualified', 'Potential', 'No answer', 'Not qualified', 'Meeting', 'Deal'];

/* Client-facing columns first, marketing columns last. */
var COLUMNS = [
  ['Date', 'date'], ['Name', 'name'], ['Phone', 'phone'], ['Project', 'project'], ['Unit Type', 'unit'],
  ['Status', '_status'], ['Deal Value (EGP)', '_blank'], ['Notes', '_blank'],
  ['Page', 'page'], ['Language', 'lang'], ['CTA', 'cta'], ['Country', 'country'],
  ['gclid', 'gclid'], ['gbraid', 'gbraid'], ['wbraid', 'wbraid'],
  ['utm_source', 'utm_source'], ['utm_medium', 'utm_medium'], ['utm_campaign', 'utm_campaign'],
  ['utm_term', 'utm_term'], ['utm_content', 'utm_content'], ['Landing', 'landing'], ['Referrer', 'referrer']
];

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
}

function setup() {
  var sh = getSheet_();
  var headers = COLUMNS.map(function (c) { return c[0]; });
  sh.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold').setBackground('#0E3B2E').setFontColor('#FFFFFF');
  sh.setFrozenRows(1);
  sh.setFrozenColumns(3);
  var rows = sh.getMaxRows() - 1;
  sh.getRange(2, 3, rows, 1).setNumberFormat('@');                    // Phone as text (keeps the +)
  sh.getRange(2, 1, rows, 1).setNumberFormat('yyyy-mm-dd hh:mm');
  sh.getRange(2, 7, rows, 1).setNumberFormat('#,##0');
  var rule = SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).setAllowInvalid(false).build();
  sh.getRange(2, 6, rows, 1).setDataValidation(rule);
  sh.getRange(1, 9, 1, headers.length - 8).setBackground('#6E7268');  // marketing columns in grey
}

/* Stops a value like "=IMPORTXML(...)" typed into the form from running as a formula. */
function clean_(v) {
  v = String(v == null ? '' : v).slice(0, 500);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var d = JSON.parse(e.postData.contents || '{}');
    if (!d.phone || !/^\+\d{7,15}$/.test(d.phone)) return out_({ ok: false });
    var sh = getSheet_();
    if (sh.getLastRow() === 0) setup();
    var row = COLUMNS.map(function (c) {
      if (c[1] === 'date') return new Date();
      if (c[1] === '_status') return 'New';
      if (c[1] === '_blank') return '';
      if (c[1] === 'phone') return d.phone;
      return clean_(d[c[1]]);
    });
    var r = sh.getLastRow() + 1;
    sh.getRange(r, 3).setNumberFormat('@');
    sh.getRange(r, 1, 1, row.length).setValues([row]);
    notify_(d);
    return out_({ ok: true });
  } catch (err) {
    console.error(err);
    return out_({ ok: false });
  } finally {
    lock.releaseLock();
  }
}

function notify_(d) {
  var subject = 'New lead — ' + (d.project || 'VIBE') + (d.unit ? ' / ' + d.unit : '') + ' — ' + (d.name || '');
  var wa = 'https://wa.me/' + String(d.phone).replace(/\D/g, '');
  var lines = [
    'Name: ' + (d.name || ''),
    'Phone: ' + d.phone + '   (WhatsApp: ' + wa + ')',
    'Project: ' + (d.project || ''),
    'Unit type: ' + (d.unit || ''),
    '',
    'Page: ' + (d.page || '') + ' [' + (d.lang || '') + ']',
    'CTA: ' + (d.cta || ''),
    'Campaign: ' + (d.utm_campaign || '-') + ' | Source: ' + (d.utm_source || '-') + ' | Keyword: ' + (d.utm_term || '-'),
    'Google click id: ' + (d.gclid || d.gbraid || d.wbraid ? 'yes' : 'no'),
    '',
    'Sheet: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl()
  ];
  MailApp.sendEmail({ to: EMAIL_TO, cc: EMAIL_CC, subject: subject, body: lines.join('\n') });
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() { return out_({ ok: true, service: 'vibe-leads' }); }
