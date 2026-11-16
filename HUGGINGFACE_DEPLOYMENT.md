# Hosting TaxMate on Hugging Face Spaces (100% Free)

This guide shows you how to host the TaxMate backend completely for free using **Hugging Face Spaces** (Free CPU Tier: 2 vCPU, 16 GB RAM) and **MongoDB Atlas** (Free M0 Sandbox: 512 MB).

---

## Step 1: Set up Free MongoDB Atlas Database

Since Hugging Face Spaces runs only your application container, you need a free cloud MongoDB database:

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign in/register (Free).
2. Create a new cluster and select **M0 Free**.
3. Under **Security > Database Access**:
   - Create a database user (e.g., `taxmate_admin`) and set a password.
4. Under **Security > Network Access**:
   - Click **Add IP Address** -> select **Allow Access from Anywhere** (`0.0.0.0/0`) so Hugging Face can connect.
5. Under **Deployment > Database**:
   - Click **Connect** -> Choose **Drivers (Python)**.
   - Copy your connection string, which looks like:
     ```
     mongodb+srv://taxmate_admin:<password>@cluster0.abcde.mongodb.net/taxmate_db?retryWrites=true&w=majority
     ```
   *(Replace `<password>` with your database user password).*

---

## Step 2: Create a Hugging Face Space

1. Log in to [Hugging Face](https://huggingface.co/).
2. Click on your profile icon (top right) -> **New Space** (or go to [https://huggingface.co/new-space](https://huggingface.co/new-space)).
3. Configure the Space:
   - **Space Name**: `taxmate-backend` (or any name you like)
   - **License**: `mit`
   - **Space SDK**: Choose **Docker**
   - **Template**: Choose **Blank**
   - **Space Hardware**: **CPU basic • 2 vCPU • 16 GB RAM • Free**
   - **Visibility**: **Public** (recommended so your frontend can access it)
4. Click **Create Space**.

---

## Step 3: Add Secrets (Environment Variables) in Hugging Face

1. In your newly created Space, navigate to **Settings** > **Variables and secrets**.
2. Click **New secret** and add each of these:

| Secret Name | Value |
|---|---|
| `MONGODB_URI` | Your MongoDB Atlas connection URI from Step 1 |
| `DB_NAME` | `taxmate_db` |
| `GOOGLE_API_KEY` | Your Google Gemini API Key |
| `OPENROUTER_API_KEY` | Your OpenRouter API Key |
| `LLAMA_CLOUD_API_KEY` | Your Llama Cloud API Key (if used) |
| `ENVIRONMENT` | `production` |

---

## Step 4: Push Code to Hugging Face Spaces

Open your terminal in `d:\tax\TaxMate_filing-automation-` and run:

```powershell
# 1. Commit the changes
git add .
git commit -m "Configure backend for free Hugging Face Spaces deployment"

# 2. Add Hugging Face as a git remote
# Replace YOUR_USERNAME and YOUR_SPACE_NAME with your HF details
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/taxmate-backend

# 3. Push to Hugging Face
git push hf HEAD:main
```

*(When asked for a password, generate a Hugging Face User Access Token with **Write** permission at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and paste it as the password).*

---

## Step 5: Verify Your API

Once the build finishes in your Hugging Face Space:
- **Base API URL**: `https://YOUR_USERNAME-taxmate-backend.hf.space`
- **Interactive Swagger Docs**: `https://YOUR_USERNAME-taxmate-backend.hf.space/docs`
- **Health Check**: `https://YOUR_USERNAME-taxmate-backend.hf.space/` (returns `{"status":"running","service":"TaxMate API"}`)
