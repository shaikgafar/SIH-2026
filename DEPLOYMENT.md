# 🚀 LunaAlign (SIH26166) - Deployment Guide

This guide covers 5 simple ways to deploy and run **LunaAlign** in production for your Smart India Hackathon presentation.

The project is structured with a **unified production architecture**: FastAPI serves both the REST API (`/api/...`) and the compiled React SPA (`/`) from a **single port**, eliminating CORS issues and container complexity.

---

## 🌟 Option 1: 1-Click Local Production Server (Zero Setup)

Double-click **`run_production.bat`** in the root directory, or run:

```cmd
run_production.bat
```

What it does:
1. Compiles the React frontend using `npm run build`.
2. Launches the FastAPI production server on `http://localhost:8001`.
3. Opens `http://localhost:8001` in your browser.
4. Serves the full interactive UI and API from a single server process.

---

## 🌐 Option 2: Free Cloud Deployment on Render.com (Recommended for Hackathons)

Render provides free cloud web service hosting with automatic HTTPS.

### Steps:
1. Push this repository to **GitHub** (or GitLab).
2. Go to **[https://dashboard.render.com/](https://dashboard.render.com/)** and log in.
3. Click **New +** ➔ **Web Service**.
4. Connect your GitHub repository.
5. Select **Docker** as the Runtime (or Render will automatically detect the included `render.yaml` / `Dockerfile`).
6. Click **Create Web Service**.
7. In ~2 minutes, your project will be live at a public HTTPS URL (e.g. `https://lunaalign.onrender.com`).

---

## 🚂 Option 3: Free Cloud Deployment on Railway.app

Railway detects the included `railway.json` and `Dockerfile` automatically.

### Steps:
1. Go to **[https://railway.app/](https://railway.app/)** and log in with GitHub.
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Select your `SIH 2026` / `lunaalign` repository.
4. Click **Deploy Now**.
5. Once built, go to **Settings** ➔ **Generate Domain** to get your public HTTPS URL (e.g. `https://lunaalign-production.up.railway.app`).

---

## 🤗 Option 4: Free Hugging Face Spaces (Docker Space)

Hugging Face Spaces is great for AI/ML/CV projects.

### Steps:
1. Go to **[https://huggingface.co/spaces](https://huggingface.co/spaces)** and click **Create new Space**.
2. Space Name: `lunaalign-sih26166`
3. License: `mit` / `apache-2.0`
4. Space SDK: Select **Docker** ➔ **Blank**.
5. Push the files in this directory to your Hugging Face Space git repository.
6. The multi-stage `Dockerfile` will automatically build the React app and launch on port `7860` (or set `PORT=7860`).

---

## 🐳 Option 5: Self-Hosted Docker / VPS / Cloud VM

If you have Docker Desktop or an AWS/DigitalOcean/GCP virtual machine:

```bash
# Build and run with Docker Compose:
docker compose up --build -d

# Or with raw Docker:
docker build -t lunaalign:latest .
docker run -d -p 8001:8001 --name lunaalign lunaalign:latest
```

The portal will be accessible at `http://<your-server-ip>:8001`.

---

## ⚡ Option 6: Instant Live Share URL (For Demo to Judges Right Now)

If your local server is running on `http://localhost:8001`, you can instantly generate a temporary public URL that anyone in the world (e.g. hackathon judges) can open on their laptop or mobile phone:

In a new terminal, run:
```bash
npx localtunnel --port 8001
```
It will output a live public URL like:
```
your url is: https://funny-moon-42.loca.lt
```
Share this link with anyone for instant access to your running LunaAlign dashboard!
