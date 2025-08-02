# **OxygenNet** 🌐✨  
**راه‌حلی هوشمند برای دسترسی آزاد به اینترنت**  

<p align="center">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8%2B-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen.svg" alt="Status">
</p>

---

## **📌 معرفی**  
OxygenNet یک سیستم **استخراج و توزیع خودکار** کانفیگ‌های امن (V2Ray/WireGuard) از منابع عمومی است که:  
✅ **کانفیگ‌های معتبر** را جمع‌آوری و بررسی می‌کند  
✅ **بدون محدودیت** در اختیار همه قرار می‌دهد  
✅ **به‌روزرسانی خودکار** ساعتی دارد  

> **شعار ما**: اینترنت آزاد، مثل اکسیژن باید برای همه رایگان باشد!  

---

## **✨ ویژگی‌های کلیدی**  
- 🔄 **استخراج خودکار** از کانال‌های تلگرام  
- 📦 **ذخیره‌سازی ساختاریافته** (JSON + فایل‌های متنی)  
- 🚀 **API ساده** برای دریافت کانفیگ‌ها  
- 🛡️ **حریم خصوصی** (عدم ذخیره لاگ کاربران)  
- 🐳 **پشتیبانی از Docker** برای نصب آسان  

---

## **🚀 شروع سریع**  

### **پیش‌نیازها**  
- Python 3.8+  
- Docker (اختیاری)  

### **نصب با Docker**  
```bash
docker-compose up --build
```

### **نصب دستی**  
```bash
git clone https://github.com/unknownmsv/OxygenNet.git
cd OxygenNet
pip install -r requirements.txt
python main.py
```

---

## **🧩 معماری پروژه**  
```
oxygennet/
├── core/            # هسته اصلی
│   ├── miner.py     # استخراج کانفیگ‌ها
│   └── sub_api.py   # سرور اشتراک‌گذاری
├── configs/         # ذخیره کانفیگ‌ها
├── docker-compose.yml
└── README.md
```

---

## **🌍 API استفاده**  
دریافت لیست کانفیگ‌ها:  
```bash
GET /sub
```
مثال خروجی:  
```json
{
  "status": "success",
  "configs": [
    {"id": 1, "type": "vmess", "config": "..."}
  ]
}
```

---

## **🤝 مشارکت**  
ما از مشارکت شما استقبال می‌کنیم!  
- گزارش باگ در [Issues](https://github.com/your-repo/issues)  
- ارسال Pull Request برای بهبود کد  

---

## **📜 لایسنس**  
این پروژه تحت **[Apache License 2.0](LICENSE)** منتشر شده است.  

---  
<p align="center">
  <a href="https://github.com/your-repo">🌐 وبسایت</a> •
  <a href="https://t.me/oxygennet_support">💬 گروه پشتیبانی</a>
</p>

**راه آزادی اینترنت را با ما ادامه دهید!** 🔓
