# Runbook — موقع مشاريع لبروكر (Landing pages + SEO + AEO + Tracking + Search campaign)

النسخة الأولى: أكتوبر 2026، مبنية على مشروع VIBE Real Estate (`Muhaabdo/the-polygon-s`).
الاستخدام: ارفع الملف ده في أي بروجكت جديد، وقول لـ Claude: "اتبع الـ runbook ده للعميل الجديد".

---

## 0. قواعد ثابتة
- HTML + CSS + JS فقط (من غير page builder). الصفحات **بتتولّد** من ملف داتا واحد بسكريبت Python، مش بتتكتب بإيد.
- **نقطة البداية في الكود:** clone لـ `Muhaabdo/the-polygon-s` وإعادة استخدام `tools/build.py` و `tools/site_data.py` و `tools/pages_data.py` و `assets/js/project.js` و `assets/js/countries.js` و `assets/css/project.css`. نغيّر الداتا والبراند، مش نعيد البناء من الصفر.
- عربي على الروت، إنجليزي تحت `/en/`. أسماء المشاريع والوحدات بالإنجليزي في اللغتين.
- أي سعر أو خصم أو معلومة مشروع لازم يكون من الشيت أو من Abdo. لو مش متأكد: سيبه برّه الصفحة والإعلان واسأل.
- العميل **وسيط مستقل، مش المطوّر.** ده بيتقال في الرئيسية و"من نحن" والفوتر والـ FAQ. ده اللي بيحمي حساب الإعلانات.
- التسليم على مراحل: صفحة واحدة الأول للمراجعة، وبعدين الباقي.

## 1. المدخلات (Abdo بيبعتها)
| المدخل | ملاحظات |
|---|---|
| شيت الأسعار / Availability من المطوّر | Claude يستخرج منه أقل سعر لكل نوع وحدة والمساحات. الـ Grand Total = السعر الكامل قبل الخصم |
| أسماء المشاريع المطلوبة | ومين فيهم ليه صفحة لوحده |
| خطط السداد والعروض | من Abdo، مش من مواقع البروكرز |
| بيانات العميل | اسم البراند، الدومين، رقم الواتساب، رقم الاتصال، إيميلات الليدز (أساسي + CC)، اللوجو والألوان لو موجودة |
| الحسابات | GTM container ID، Google Ads ID + conversion label، الـ GA4 property (أو هنعمل واحدة) |
| الصور | من Abdo أو من موقع المطوّر. ممنوع صور عليها watermark لبروكر تاني |

## 2. هيكل الموقع
- **صفحة لكل مشروع:** `/project-slug`
- **صفحة مجمّعة للمطوّر أو المنطقة:** مثلًا `/palm-hills-october`. دي اللي بتستهدف الكلمة العامة، والإعلانات العامة بتودّي عليها.
- **الرئيسية:** هوية العميل كوسيط مستقل + كروت المشاريع + أسئلة عامة. معلوماتية مش بيع.
- **من نحن** و**سياسة الخصوصية** (لازمين لسياسات جوجل).
- **صفحة الشكر** (noindex) و **404**.

### أقسام صفحة المشروع (بالترتيب)
1. Hero: اسم المشروع، المنطقة، "يبدأ من"، المقدم والتقسيط، زرار CTA.
2. الوحدات والأسعار: كارت لكل نوع (المساحة، السعر، التشطيب، زرار CTA عليه نوع الوحدة).
3. نبذة + مميزات (6) + أرقام سريعة.
4. اللوكيشن + المسافات (من مصدر موثوق فقط).
5. الجاليري (لو فيه صورتين أو أكتر).
6. مشاريع تانية (كاروسيل) + لينك للصفحة المجمّعة.
7. FAQ (متولّد من الداتا).
8. فورم ختامي + رقم الاتصال.
9. فوتر: disclaimer + "مش المطوّر" + لينك الخصوصية.
+ شريط CTA ثابت على الموبايل، وزرار اللغة جوه الناف بار في الموبايل.

### أقسام الصفحة المجمّعة
Hero ← كروت المشاريع ← جدول مقارنة ← "أنهي مشروع يناسبك" (شقق / Family homes وتاون / توين وفيلات بأقل سعر لكل نوع) ← عن المنطقة أو المطوّر ← FAQ ← فورم فيه اختيار المشروع.

## 3. فلو الليد (ثابت)
زرار "تفاصيل أكثر - واتساب" → فورم (اسم + كود دولة بالأعلام + رقم + نوع الوحدة أو المشروع) → Google Sheet + إيميل (Apps Script) → صفحة شكر (conversion) → واتساب برسالة جاهزة فيها المشروع والوحدة.
- الفورم بيقول صراحة إنه هيتحوّل لواتساب وإن العميل موافق يتم التواصل معاه، ولينك الخصوصية.
- ديسكتوب: واتساب في تاب جديد. موبايل: نفس التاب بعد 1.8 ثانية.
- تحقق الرقم: جدول الدول، ومصر `^1[0125]\d{8}$`، ورفض الأرقام المكررة.
- حفظ gclid / gbraid / wbraid / UTMs لمدة 90 يوم وإرسالها مع الليد.
- **الشيت:** أعمدة العميل الأول (Date, Name, Phone, Project, Unit Type, Status, Deal Value, Notes) وبعدها أعمدة التسويق. Status: New / Qualified / Potential / No answer / Not qualified / Meeting / Deal.

## 4. التتبع
**dataLayer events:** `cta_click`، `form_open`، `form_start`، `form_error`، `form_close`، `generate_lead`، `thank_you_view` (مرة واحدة لكل ليد)، `whatsapp_redirect`، `call_click`، `project_switch`.
Params: `project`، `unit_type`، `cta_location`، `form_location`، `page_lang`.
- `form_open` بيتحسب كمان لما الفورم اللي تحت يظهر على الشاشة (`form_location = final_form`). يتقرا مقسوم بـ form_location.

**GTM:** import للـ JSON (`tools/gtm/vibe-gtm-import.json`) بـ **Merge مش Overwrite**. بعدها:
- حط الـ Measurement ID في constant `GA4 - Measurement ID`.
- تاج Google Ads conversion على trigger `CE - thank_you_view`.
- Conversion Linker على All Pages.
- Preview على الموقع وتأكيد إن كل الـ funnel Fired قبل النشر.

**GA4:**
- Enhanced measurement: اقفل **Form interactions** (بتكرر form_start).
- Custom dimensions (Event): project، unit_type، cta_location، form_location، page_lang.
- Key event: `generate_lead` من غير قيمة افتراضية.
- Audiences: زوار كل مشروع ومسجلوش (90 يوم)، زوار الصفحة المجمّعة (90)، Leads (أقصى مدة)، Form started no lead (30)، Form opened not started (30)، CTA clicked no lead (30).
- ربط بـ Google Ads + Personalized advertising + Google signals.

**Google Ads:** هدف Submit lead form = account default و Primary، والمكالمات Secondary، وأي تحويل قديم ملوش تاج يتشال.

## 5. SEO
- Title ≤ 60 حرف فيه اسم المشروع + الكلمة اللي الناس بتبحث بيها بالعربي (مثلًا "بامبو 3") + "الأسعار 2026". Description بالسعر والمقدم والتقسيط.
- canonical لكل صفحة، hreflang (ar / en / x-default)، lang و dir صح.
- Schema: RealEstateAgent، WebPage، BreadcrumbList (الرئيسية ← المجمّعة ← المشروع)، ApartmentComplex للمشروع، FAQPage، ItemList في المجمّعة.
- og:image بمقاس 1200×630 JPG لكل صفحة + og:image:width/height/alt.
- `favicon.ico` في الروت + SVG.
- `sitemap.xml` (urlset بسيط) و `robots.txt` (Disallow لصفحة الشكر و `/tools/`).
- 301 لأي رابط قديم للصفحة الأقرب (`.htaccess` لـ Hostinger + `vercel.json` للتست).
- Alt لكل صورة، lazy loading، و preload لصورة الـ hero.

## 6. AEO (الظهور في ChatGPT / Gemini / AI Overviews)
- FAQ لكل مشروع متولّد من الداتا: المكان، الأسعار، خطط السداد، الوحدات والمساحات، الاستلام، التشطيب، مين المطوّر، هل الأسعار نهائية.
- `llms.txt` في الروت: تعريف العميل كوسيط مستقل + كل مشروع بجدول وحداته وأسعاره وأسئلته.
- جمل واقعية قصيرة بالأرقام بدل الكلام التسويقي.
- **Bing Webmaster** مهم (ChatGPT بيعتمد عليه)، و Google Business Profile للعميل كمصدر لينك وهوية.
- لا ضمانات: ده بيرفع الفرصة، مش بيضمن الظهور.

## 7. ملف الحملة
`tools/ads/build_campaign.py` → CSV لـ Google Ads Editor + xlsx للمراجعة.
- حملة Search واحدة في الأول (عشان الداتا تتجمع)، ad group لكل مشروع × لغة + ad group للمجمّعة.
- Phrase + Exact فقط، من غير broad.
- **Negatives من أول يوم:** إيجار/ريسيل، وظائف، خدمة عملاء المطوّر، النادي/البورصة، وحدات تجارية، **وكل المناطق والمشاريع التانية للمطوّر** (التجمع، زايد، العلمين، السخنة، العاصمة، الساحل، أسماء المشاريع اللي مش عندنا).
- الـ ad group العام عليه negatives بأسماء المشاريع.
- **ممنوع** كلمات عامة من غير منطقة زي "مشاريع [المطوّر]" (دي أكلت نص ميزانية VIBE في يومين).
- RSA: 15 headline (الأول متثبت باسم المشروع) + 4 descriptions، كلها جوه الحدود. مفيش خصم في الإعلان قبل ما يتأكد من المطوّر.
- Bidding: Maximize clicks بـ max CPC، وبعد 15–20 ليد → Maximize conversions.

## 8. QA قبل التسليم
- [ ] كل الصفحات موبايل (360/390) وديسكتوب من غير horizontal scroll.
- [ ] كل اللينكات الداخلية 200، ومفيش صور مكسورة.
- [ ] ليد تجريبي من كل نوع فورم: وصل الشيت + الإيميل للعنوانين + صفحة الشكر + واتساب.
- [ ] GTM Preview: الـ funnel كله Fired، و `Lead Form` مرة واحدة.
- [ ] Facebook Sharing Debugger: الصورة والعنوان صح.
- [ ] Schema صالح (Rich Results Test).
- [ ] الأسعار في الصفحات والـ FAQ والإعلانات مطابقة للشيت.

## 9. الإطلاق
1. رفع على Hostinger (الفولدر كله ما عدا `tools/` و `data/`).
2. Search Console: **URL-prefix property** (الـ Domain property ممكن تعلق على "Couldn't fetch") + إرسال الـ sitemap + Request indexing للرئيسية والمجمّعة والمشاريع.
3. Bing Webmaster: Import من Search Console + إرسال الـ sitemap + URL submission.
4. ربط Search Console بـ GA4.
5. Scrape Again في Facebook debugger للصفحات الأساسية.
6. الحملة تتعمل Paused، تتراجع، وبعدين تشتغل.

## 10. المتابعة
- يوم 2–3: تقرير Search terms → negatives جديدة.
- أسبوعيًا: الـ funnel في GA4 مقسوم بـ form_location، وتكلفة الليد لكل مشروع.
- شهريًا: Status و Deal Value من الشيت → أنهي مشروع بيجيب meetings وبيع فعلًا. ده الرقم اللي بيتعرض على العميل.
- بعد ~أسبوع: Request indexing تاني لأي صفحة "Crawled – not indexed".
