# LEADER_GAMES — موقع أخبار الألعاب (PC / Console / Mobile)

صاحب الموقع: leader-vi7

موقع ثابت (HTML + CSS + JS) يعرض عناوين وملخصات قصيرة لأخبار الألعاب من:
IGN، GameSpot، Eurogamer، GamesRadar+، Kotaku، Gematsu — مع رابط للمقال الأصلي.

التحديث تلقائي: GitHub Actions يشغّل `scripts/fetch_news.py` كل 30 دقيقة، يجلب الخلاصات (RSS)، ثم ينشر الموقع على GitHub Pages. لا تحتاج لأي تدخل.

## خطوات النشر (مرة واحدة، حوالي 10 دقائق)

1. أنشئ حساباً مجانياً على https://github.com ثم مستودعاً جديداً (New repository) باسم مثلاً `leader-games`، واجعله **Public**.
2. ارفع كل ملفات هذا المجلد إلى المستودع (Add file ← Upload files)، **بما فيها المجلد المخفي `.github`**.
   - إن لم يظهر لك المجلد المخفي عند السحب والإفلات، أنشئ الملف يدوياً: Add file ← Create new file، واكتب في الاسم `.github/workflows/update-and-deploy.yml` والصق محتواه.
3. من المستودع: Settings ← Pages ← في خانة **Source** اختر **GitHub Actions**.
4. من تبويب **Actions** افتح "Update news and deploy" ثم Run workflow (أو ادفع أي تعديل).
5. بعد دقيقتين يظهر رابط موقعك: `https://USERNAME.github.io/leader-games/`

بعد ذلك يتحدث الموقع وحده كل 30 دقيقة.

## دومين خاص (اختياري)
Settings ← Pages ← Custom domain، ثم اربط الدومين من عند مزوّده (سجل CNAME إلى `USERNAME.github.io`).

## تخصيصات
- تغيير مدة التحديث: عدّل `cron` في `.github/workflows/update-and-deploy.yml` (لا تقل عن 15 دقيقة).
- إضافة/حذف مصدر: عدّل القاموس `SOURCES` في `scripts/fetch_news.py`.
- تحسين تصنيف المنصات: عدّل `PLATFORM_KEYWORDS` في نفس الملف.
- إن فشل مصدر ما، يتخطاه السكربت ويكمل بالباقي (انظر سجل Actions لعدد الأخبار من كل مصدر).

## ملاحظة قانونية
الموقع يعرض العنوان وملخصاً قصيراً (≈200 حرف) وصورة المصدر مع رابط مباشر للمقال الأصلي ويذكر اسم الموقع. لا تنسخ المقالات كاملة. راجع شروط استخدام كل موقع قبل أي إعلانات أو استخدام تجاري.
