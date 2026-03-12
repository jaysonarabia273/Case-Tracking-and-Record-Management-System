# Render Deployment Guide for CaseTracking

## Step 1: Push Your Project to GitHub

First, you need to push your project to a GitHub repository (Render deploys from Git).

### If you haven't initialized Git yet:
```bash
cd C:\Users\Arabia\OneDrive\Desktop\casetracking-main\casetracking-main\Capstone
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/casetracking.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username, and create the repository at `https://github.com/new` first.

---

## Step 2: Create a Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended - easier deployment)
3. Log in

---

## Step 3: Deploy on Render

1. Click **"+ New +"** button
2. Select **"Web Service"**
3. Connect your GitHub repository (search for "casetracking")
4. Fill in:
   - **Name**: `casetracking-app` (or any name)
   - **Runtime**: Python 3.11 (auto-selected)
   - **Build Command**: `pip install -r requirements.txt && python Capstone/manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn Capstone.Capstone.wsgi:application --bind 0.0.0.0:$PORT --workers 4`
   - **Root Directory**: `Capstone` (leave blank if at root of repo)
5. Click **"Create Web Service"**

---

## Step 4: Add Environment Variables

Go to your Render service dashboard → **Environment** tab:

Add these variables:
- `DEBUG`: `False`
- `DATABASE_URL`: Leave empty (Render will auto-generate if you add PostgreSQL)
- `ALLOWED_HOSTS`: `*.onrender.com`
- `SECRET_KEY`: (Render auto-generates)
- `DB_NAME`: `casetracking`
- `DB_USER`: `postgres`
- `DB_PASSWORD`: (Any password you choose)
- `DB_HOST`: (Render auto-fills after PostgreSQL is added)
- `DB_PORT`: `5432`

---

## Step 5: Add PostgreSQL Database (Optional but Recommended)

1. In Render dashboard, click **"+ New"** → **"PostgreSQL"**
2. Create a free PostgreSQL instance
3. Render will auto-add the `DATABASE_URL` to your service environment

---

## Step 6: View Your Public URL

After deployment completes:
- Your app will be at: `https://casetracking-app.onrender.com` (or your chosen name)
- Students can access it from mobile data any time
- QR code will point to this permanent URL

---

## Step 7: Update QR Code

Once you have your Render URL, update the QR file:

1. Edit: `Capstone/tools/qr-url.txt`
2. Replace content with: `https://casetracking-app.onrender.com`
3. Run the QR generator:
   ```powershell
   & "C:/Users/Arabia/OneDrive/Desktop/casetracking-main/casetracking-main/Capstone/venv/Scripts/python.exe" "C:/Users/Arabia/OneDrive/Desktop/casetracking-main/casetracking-main/Capstone/tools/make_qr.py"
   ```

Your QR is now permanent and works on mobile data!

---

## Troubleshooting

**Build failed?**
- Check Render logs (Dashboard → Logs tab)
- Make sure `requirements.txt` is at repo root or adjust paths

**Can't access database?**
- Verify `DATABASE_URL` environment variable exists
- Make sure PostgreSQL instance is created

**App crashes on startup?**
- Check migrations: `python Capstone/manage.py migrate`
- Verify all environment variables are set

---

## Notes

- Free tier has some limitations (sleeps after 15 min inactivity, restarts monthly)
- If you need better uptime, consider Render's paid plans ($7+/month)
- Database is included free for small projects
