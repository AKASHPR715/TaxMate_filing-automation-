# 🍎 Run TaxMate on Mac (Beginner's Guide)

This guide takes you from zero to running the TaxMate application on your macOS machine. No prior experience needed!

## 📋 Prerequisites (What you need installed)

1.  **Docker Desktop** (The engine that runs the app)
    *   **Download**: [Click here to download Docker Desktop for Mac](https://rubikscode.net/wp-content/uploads/2021/05/screen-shot-2021-05-24-at-9.37.23-am.png) (Choose "Apple Chip" for M1/M2/M3 or "Intel Chip" for older Macs).
        *   *Official Link*: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    *   **Install**: Drag the Docker icon to Applications.
    *   **Start**: Open "Docker" from your Applications folder. You should see a whale icon in your top menu bar.

2.  **Git** (Usually comes with Mac, but if not...)
    *   Open Terminal (Cmd + Space, type "Terminal").
    *   Type `git --version`. If it asks to install command line tools, say "Install".

3.  **MongoDB Compass** (Optional - to see your data)
    *   **Download**: [Click here to download MongoDB Compass](https://www.mongodb.com/try/download/compass)
    *   **Install**: Open the DMG file and drag Compass to Applications.

---

## 🏃 Step-by-Step Instructions

### Step 1: Get the Code
1.  Open **Terminal** (Cmd + Space, type "Terminal").
2.  Navigate to your Desktop (or where you want to put the project):
    ```bash
    cd Desktop
    ```
3.  Clone the project (download it):
    ```bash
    git clone <YOUR_REPOSITORY_URL_HERE>
    cd TaxMate_filing-automation-
    ```

### Step 2: Configure Keys (One-time Setup)
1.  In the project folder, make a copy of the example config:
    ```bash
    cp .env.example .env
    ```
2.  Open the file to edit it:
    ```bash
    open -e .env
    ```
    (This opens it in TextEdit).
3.  **Crucial**: You must fill in your API keys for the app to work!
    *   `LLAMA_CLOUD_API_KEY=rr-k-...` (Required for PDF extraction)
    *   `OPENROUTER_API_KEY=sk-...` (Required for AI Tax Advisor)
4.  Save (Cmd+S) and close TextEdit.

### Step 3: Run the App!
1.  Back in your Terminal (ensure you are inside `TaxMate_filing-automation-` folder), run this command:
    ```bash
    docker compose up --build
    ```
    *(Note: The first time you run this, it will take 5-10 minutes to download everything. Grab a coffee! ☕)*

2.  Wait until you see logs stopping and messages like `Application startup complete` or `Uvicorn running on ...`.

### Step 4: Use TaxMate
*   **Frontend (The App)**: Open Safari/Chrome and go to: [http://localhost:3000](http://localhost:3000)
*   **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 5: See Your Data (Optional)
If you installed MongoDB Compass:
1.  Open **MongoDB Compass**.
2.  In the URI field, paste: `mongodb://localhost:27017`
3.  Click **Connect**.
4.  You will see `tax_filing` database with all your user data and forms!

---

## 🛑 How to Stop
To stop the application, press `Ctrl + C` in the terminal where it's running.
To clean up completely:
```bash
docker compose down
```

## ❓ Troubleshooting Common Issues

*   **Error: "Bind for 0.0.0.0:xxxx failed: port is already allocated"**
    *   **Solution**: Disable "AirPlay Receiver" in System Settings -> General -> AirDrop & Handoff (it uses port 5000/7000, sometimes conflicts). Or check if you have another server running.
*   **AI/Models not working?**
    *   The app automatically downloads AI models on startup. Check the logs for "pulling nomic-embed-text" progress. It might take a minute on first launch.
