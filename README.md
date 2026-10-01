# MilkMart - Modern Farm-Fresh Dairy E-Commerce Platform

A robust, full-featured, and modern light-themed dairy e-commerce web platform built with Django. MilkMart brings the farm-to-table experience online with pure organic milk, artisanal bilona ghee, fresh malai paneer, natural curd, and cold-chain morning deliveries.

---

## 🌟 Key Upgrades & Features

### 🎨 Modern Light Aesthetics & UI
- **Fresh Organic Dairy Palette**: Crisp clean whites, fresh emerald green (`#059669`), warm golden amber butter accents (`#f59e0b`), and soft dairy cream highlights.
- **Glassmorphism Header**: Sticky translucent navbar (`backdrop-filter: blur(12px)`), live cart & wishlist counter badges, instant search bar, category dropdown, and user avatar menu.
- **Engaging Hero Section**: Headline with organic dairy value proposition, morning delivery promises, live stats banner (100% Organic, 4°C Cold Chain, 60-min delivery, 25k+ families), and interactive banner carousel.
- **Product Card Suite**: Modern card layouts with hover elevation, product tags (`15% OFF`), star ratings, interactive heart wishlist toggle, and quick "Add to Cart" button.
- **Interactive Cart & Steppers**: Dynamic quantity updates (`+` / `-`) via AJAX, real-time subtotal/shipping updates, free delivery threshold progress tracker, and clean order breakdown.
- **Resilient Checkout**: Select saved delivery addresses, choose between **Cash on Delivery / Instant Demo Checkout** (guaranteed 100% working in all demo/deployed environments) or **Razorpay Online Gateway**.
- **Customer Dashboard**: Visual order tracking stepper (`Accepted` &rarr; `Packed` &rarr; `On The Way` &rarr; `Delivered`), saved address management with Edit/Delete, dedicated Wishlist page, and account settings.

### 🚀 Production Deployment Ready
- **WhiteNoise Integration**: Efficient static files compression and caching out of the box in production.
- **12-Factor App Settings**: Configurable through `.env` via `python-dotenv` (`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`).
- **Gunicorn WSGI Server**: Pinned in `requirements.txt` and wired in `Procfile`.
- **Cloud Blueprints**: Includes `Procfile`, `build.sh`, `render.yaml`, and `runtime.txt` for 1-click deployments to **Render**, **Railway**, or **Dokku**.

---

## 🛠️ Tech Stack
- **Backend**: Django 5.x / 6.x (Python 3.12 / 3.13)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), Bootstrap 5.3.3, FontAwesome 6, jQuery 3.7.1
- **Storage & Static**: WhiteNoise with Compressed Storage
- **Payments**: Razorpay Gateway + Cash on Delivery / Direct Demo Checkout fallback

---

## 💻 Local Quickstart

### 1. Clone & Enter Project
```bash
git clone <repo-url>
cd Milkmart_Platform
```

### 2. Activate Virtual Environment
```bash
# Using existing .venv
.venv\Scripts\activate

# Or create fresh environment:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy `.env.example` to `ecomm/.env`:
```bash
cp ecomm/.env.example ecomm/.env
```

### 4. Run Migrations & Start Server
```bash
cd ecomm
python manage.py migrate
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser!
Visit **http://127.0.0.1:8000/admin** for admin login

---

## 🌐 Cloud Deployment Guide

### Deploying to Render.com (Recommended - Free Tier)
1. Push this repository to **GitHub**.
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New + &rarr; Web Service**.
3. Connect your repository.
4. Set the following settings:
   - **Environment**: `Python`
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd ecomm && gunicorn ecomm.wsgi:application`
5. Under **Environment Variables**, add:
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `ALLOWED_HOSTS`: `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`
6. Click **Create Web Service** — Render will automatically build, collect static assets, run migrations, and launch your live website!

### Deploying to Railway.app
1. Click **New Project &rarr; Deploy from GitHub repo**.
2. Railway detects the `Procfile` and `requirements.txt` automatically.
3. Add your environment variables (`SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=*`).
4. Generate a public domain and deploy.

---

## 🔐 Admin Dashboard
Access the administrative portal at `/admin/` to add products, adjust categories, inspect customer addresses, and update order statuses.
