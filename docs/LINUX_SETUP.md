# 🐧 Run TaxMate on Linux (Beginner's Guide)

This guide takes you from zero to running the TaxMate application on your Linux machine. No prior experience needed!

## 📋 Prerequisites (What you need installed)

1.  **Docker & Docker Compose** (The engine that runs the app)
    *   **Install**: 
        *   **Ubuntu/Debian**:
            ```bash
            sudo apt-get update
            sudo apt-get install docker.io docker-compose-plugin
            ```
        *   **Fedora/CentOS**:
            ```bash
            sudo dnf install docker docker-compose-plugin
            ```
        *   **Arch Linux**:
            ```bash
            sudo pacman -S docker docker-compose
            ```
    *   **Start Docker Service**:
        ```bash
        sudo systemctl start docker
        sudo systemctl enable docker
        ```
    *   **Permission Setup** (Optional, to run without `sudo`):
        ```bash
        sudo usermod -aG docker $USER
        # Log out and log back in for this to take effect
        ```

2.  **Git** (Likely already installed)
    *   Open Terminal.
    *   Type `git --version`. If not found, install via your package manager (e.g., `sudo apt install git`).

3.  **MongoDB Compass** (Optional - to see your data)
    *   **Download**: [Click here to download MongoDB Compass](https://www.mongodb.com/try/download/compass). Select "Linux" and your distribution (e.g., Ubuntu).
    *   **Install**: Use `dpkg` (Debian/Ubuntu) or `rpm` (RedHat/Fedora) to install the downloaded package.

---

## 🏃 Step-by-Step Instructions

### Step 1: Get the Code
1.  Open **Terminal**.
2.  Navigate to where you want to put the project:
    ```bash
    cd ~/Desktop  # or preferred directory
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
2.  Open the file to edit it (using `nano` or your favorite editor):
    ```bash
    nano .env
    ```
3.  **Crucial**: You must fill in your API keys for the app to work!
    *   `LLAMA_CLOUD_API_KEY=rr-k-...` (Required for PDF extraction)
    *   `OPENROUTER_API_KEY=sk-...` (Required for AI Tax Advisor)
4.  If using `nano`: Press `Ctrl + O` then `Enter` to save, and `Ctrl + X` to exit.

### Step 3: Run the App!
1.  Back in your Terminal (ensure you are inside `TaxMate_filing-automation-` folder), run this command:
    ```bash
    # If you didn't add your user to docker group, add 'sudo' before this command
    docker compose up --build
    ```
    *(Note: The first time you run this, it will take 5-10 minutes to download everything. Grab a coffee! ☕)*

2.  Wait until you see logs stopping and messages like `Application startup complete` or `Uvicorn running on ...`.

### Step 4: Use TaxMate
*   **Frontend (The App)**: Open Firefox/Chrome and go to: [http://localhost:3000](http://localhost:3000)
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
    *   **Solution**: Check if another service is using port 3000, 8000, or 27017. You can check with `sudo lsof -i :<port>`.
*   **"Permission denied" connecting to Docker daemon**
    *   **Solution**: Run the command with `sudo`, or follow the "Permission Setup" in Prerequisites to add your user to the docker group.
*   **AI/Models not working?**
    *   The app automatically downloads AI models on startup. Check the logs for "pulling nomic-embed-text" progress. It might take a minute on first launch.
