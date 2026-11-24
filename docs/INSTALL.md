<div dir="rtl">

# نصب و استفاده از آوند

فایل ZIP را خارج کنید. برای هر خانواده، فایل متغیر یا وزن‌های ثابت را نصب کنید. نصب هم‌زمان این دو نوع برای یک خانواده می‌تواند در فهرست فونت بعضی برنامه‌ها ورودی تکراری ایجاد کند. `Avand UI` و `Avand UI FaNum` دو خانواده‌ی جدا هستند.

اگر پروژه از نسخه‌ی ویرا استفاده می‌کند، برای مهاجرت به آوند فایل‌های فونت و CSS را جایگزین کنید و نام خانواده را در استایل‌ها از `Vira` به `Avand UI` یا از `Vira FaNum` به `Avand UI FaNum` تغییر دهید.

## ویندوز

روی فایل `TTF` راست‌کلیک کنید و `Install` را بزنید. برای نصب نسخه‌ی ثابت، وزن‌های موردنیاز را از پوشه‌ی `fonts/static` انتخاب کنید. برنامه‌ای را که از قبل باز بوده دوباره باز کنید تا فهرست فونت‌ها تازه شود.

## مک

فایل‌های `TTF` را در `Font Book` باز و نصب کنید. اگر برنامه‌ی شما محور وزن را نمایش نمی‌دهد، از فایل‌های ثابت استفاده کنید. برای بررسی فایل در `Font Book` از گزینه‌ی اعتبارسنجی فونت استفاده کنید. [راهنمای Font Book](https://support.apple.com/guide/font-book/install-and-validate-fonts-fntbk1000/mac)

## لینوکس

در محیط دسکتاپ می‌توانید فایل `TTF` را در نمایشگر فونت باز و نصب کنید. برای نصب فقط برای حساب خودتان با `Fontconfig`، دستورهای زیر را از پوشه‌ی بسته اجرا کنید.

</div>

```sh
avand_fonts="${XDG_DATA_HOME:-$HOME/.local/share}/fonts/avand"
mkdir -p "$avand_fonts"
cp fonts/variable/AvandUI-Variable.ttf "$avand_fonts/"
fc-cache -f "$avand_fonts"
fc-match "Avand UI"
```

<div dir="rtl">

برای خانواده‌ی اعداد فارسی، `AvandUIFaNum-Variable.ttf` را هم کپی کنید. برای نسخه‌ی ثابت فایل‌های دلخواه خانواده را از `fonts/static` بردارید.

## وب

پوشه‌ی `fonts/web` را با ساختار فعلی کپی کنید و برگه‌ی `variable.css` یا `static.css` را بارگذاری کنید. در نمونه‌ی زیر فایل‌ها در مسیر `/fonts/web/` قرار گرفته‌اند. برای متن فارسی، زبان و جهت سند را مشخص کنید.

</div>

```html
<html lang="fa" dir="rtl">
  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="/fonts/web/variable.css">
    <style>
      body { font-family: "Avand UI", sans-serif; }
      .amount { font-family: "Avand UI FaNum", sans-serif; }
      .tabular { font-variant-numeric: tabular-nums; }
    </style>
  </head>
  <body>
    <p>سفارش <bdi lang="en">ORDER-248</bdi> آماده‌ی ارسال است.</p>
    <p class="amount tabular">485,000 تومان</p>
  </body>
</html>
```

<div dir="rtl">

برای داده‌هایی که باید شکل رقم‌های لاتین را حفظ کنند، از خانواده‌ی استاندارد استفاده کنید. در نسخه‌ی اعداد فارسی، تغییر رقم‌ها در مرحله‌ی نمایش انجام می‌شود و رشته‌ی اصلی یکسان می‌ماند. جداکننده‌ها از متن ورودی می‌آیند. برای نمایش «۴۸۵٬۰۰۰» با جداکننده‌ی فارسی، مقدار را ابتدا با `Intl.NumberFormat("fa-IR")` قالب‌بندی کنید.

</div>
