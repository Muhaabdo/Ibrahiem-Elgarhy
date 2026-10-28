/**
 * palmhillsdev (palmhillsdev.com) — lead capture (Google Sheets + email notification).
 *
 * Setup (once), signed in as the sheet owner (info@mohabdo.com):
 *  1. Create a new Google Sheet, then Extensions → Apps Script, delete the sample code and paste this file.
 *  2. Project Settings (gear icon) → Time zone: (GMT+02:00/+03:00) Cairo. Also in the Sheet: File → Settings → Time zone: Cairo.
 *  3. Run `setup` once and accept the permissions (it writes the header row, the Status dropdown and the formats).
 *  4. Run `testEmail` once: Ibrahim gets a test email with you in CC.
 *  5. Deploy → New deployment → type: Web app → Execute as: Me, Who has access: Anyone → Deploy.
 *  6. Send the web-app URL (ends in /exec) — it goes into SITE["endpoint"] in tools/site_data.py.
 *  After any later code change: Deploy → Manage deployments → Edit → Version: New version (the URL stays the same).
 */
var SHEET_NAME = 'Leads';
var EMAIL_TO = 'ibrahimelgarhy1987@gmail.com';
var EMAIL_CC = 'info@mohabdo.com';
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
  sh.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold').setBackground('#141414').setFontColor('#FFFFFF');
  sh.setFrozenRows(1);
  sh.setFrozenColumns(3);
  var rows = sh.getMaxRows() - 1;
  sh.getRange(2, 3, rows, 1).setNumberFormat('@');                    // Phone as text (keeps the +)
  sh.getRange(2, 1, rows, 1).setNumberFormat('yyyy-mm-dd hh:mm');
  sh.getRange(2, 7, rows, 1).setNumberFormat('#,##0');
  var rule = SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).setAllowInvalid(false).build();
  sh.getRange(2, 6, rows, 1).setDataValidation(rule);
  sh.getRange(1, 9, 1, headers.length - 8).setBackground('#686868');  // marketing columns in grey
  sh.getRange(1, 1, 1, 8).setBackground('#D31148');                    // client columns in brand crimson
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
    var repeat = isRepeat_(sh, d.phone);
    var row = COLUMNS.map(function (c) {
      if (c[1] === 'date') return new Date();
      if (c[1] === '_status') return 'New';
      if (c[0] === 'Notes') return repeat ? 'Repeat — number already in sheet' : '';
      if (c[1] === '_blank') return '';
      if (c[1] === 'phone') return d.phone;
      return clean_(d[c[1]]);
    });
    var r = sh.getLastRow() + 1;
    sh.getRange(r, 3).setNumberFormat('@');
    sh.getRange(r, 1, 1, row.length).setValues([row]);
    notify_(d, repeat);
    return out_({ ok: true });
  } catch (err) {
    console.error(err);
    return out_({ ok: false });
  } finally {
    lock.releaseLock();
  }
}

/* True when this phone number already has a row (column C). */
function isRepeat_(sh, phone) {
  if (sh.getLastRow() < 2) return false;
  return !!sh.getRange(2, 3, sh.getLastRow() - 1, 1).createTextFinder(String(phone)).matchEntireCell(true).findNext();
}

function notify_(d, repeat) {
  var subject = (repeat ? 'Repeat lead — ' : 'New lead — ') + (d.project || 'palmhillsdev') + (d.unit ? ' / ' + d.unit : '') + ' — ' + (d.name || '');
  var wa = 'https://wa.me/' + String(d.phone).replace(/\D/g, '');
  var lines = [
    'الاسم / Name: ' + (d.name || ''),
    'الموبايل / Phone: ' + d.phone,
    'واتساب / WhatsApp: ' + wa,
    'المشروع / Project: ' + (d.project || 'غير محدد / not specified'),
    'نوع الوحدة / Unit: ' + (d.unit || 'استفسار عام / general enquiry'),
    repeat ? 'ملاحظة: الرقم ده سجّل قبل كده / This number is already in the sheet.' : '',
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

/* Run once from the editor to check that the email reaches Ibrahim (and you in CC). */
function testEmail() {
  notify_({ name: 'Test lead', phone: '+201000000000', project: 'Badya', unit: '2 Bedroom Apartment', page: 'https://palmhillsdev.com/badya', lang: 'ar', cta: 'test' }, false);
}

function doGet() { return out_({ ok: true, service: 'palmhillsdev-leads' }); }
