# 🚀 Run TaxMate on Windows (Beginner's Guide)

This guide takes you from zero to running the TaxMate application on your Windows machine. No prior experience needed!

## 📋 Prerequisites (What you need installed)

1.  **Docker Desktop** (The engine that runs the app)
    *   **Download**: [Click here to download Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
    *   **Install**: Run the installer.
    *   **Settings**: During install, ensure "Use WSL 2 instead of Hyper-V" is CHECKED (this is usually default).
    *   **Start**: After installing, search for "Docker Desktop" in your Start menu and open it. Wait until you see the green whale icon or "Engine running" in the bottom left.

2.  **Git** (To download the code)
     *   **Download**: [Click here to download Git](https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe)
     *   **Install**: Just keep clicking "Next" -> "Next" -> "Finish" (default settings are fine).

3.  **MongoDB Compass** (Optional - to see your data)
    *   **Download**: [Click here to download MongoDB Compass](https://www.mongodb.com/try/download/compass)
    *   **Install**: Run the installer.

---

## 🏃 Step-by-Step Instructions

### Step 1: Get the Code
1.  Open **Command Prompt** or **PowerShell** (Search for "cmd" in Windows Start menu).
2.  Navigate to your Desktop (or where you want to put the project):
    ```cmd
    cd Desktop
    ```
3.  Clone the project (download it):
    ```cmd
    git clone <YOUR_REPOSITORY_URL_HERE>
    cd TaxMate_filing-automation-
    ```

### Step 2: Configure Keys (One-time Setup)
1.  In the project folder, locate the file named `.env.example`.
2.  Copy and paste it, then rename the copy to `.env`.
3.  Open `.env` with Notepad.
4.  **Crucial**: You must fill in your API keys for the app to work!
    *   `LLAMA_CLOUD_API_KEY=rr-k-...` (Required for PDF extraction)
    *   `OPENROUTER_API_KEY=sk-...` (Required for AI Tax Advisor)
5.  Save and close the file.

### Step 3: Run the App!
1.  Back in your Command Prompt/PowerShell (ensure you are inside `TaxMate_filing-automation-` folder), run this command:
    ```cmd
    docker compose up --build
    ```
    *(Note: The first time you run this, it will take 5-10 minutes to download everything. Grab a coffee! ☕)*

2.  Wait until you see logs stopping and messages like `Application startup complete` or `Uvicorn running on ...`.

### Step 4: Use TaxMate
*   **Frontend (The App)**: Open Chrome/Edge and go to: [http://localhost:3000](http://localhost:3000)
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
```cmd
docker compose down
```

## ❓ Troubleshooting Common Issues

*   **Error: "Bind for 0.0.0.0:xxxx failed: port is already allocated"**
    *   **Solution**: Another program is using port 3000 or 8000. Close other running node apps or servers.
*   **Error: "docker is not recognized..."**
    *   **Solution**: Docker Desktop is not running or not in your PATH. Open Docker Desktop app and try again.
*   **AI/Models not working?**
    *   The app automatically downloads AI models on startup. Check the logs for "pulling nomic-embed-text" progress. It might take a minute on first launch.
