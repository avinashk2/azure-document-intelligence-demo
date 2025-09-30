# Deployment Guide - Streamlit Community Cloud

This guide walks you through deploying the Azure Document Intelligence Demo to **Streamlit Community Cloud** (free).

## Prerequisites

1. Azure Document Intelligence resource (get free tier at https://portal.azure.com)
2. GitHub account
3. Streamlit Community Cloud account (free at https://share.streamlit.io)

## Step 1: Push to GitHub

1. **Create a new repository on GitHub** (https://github.com/new)
   - Name it something like `azure-document-intelligence-demo`
   - Make it public or private (both work)
   - Don't initialize with README

2. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git add .
   git commit -m "Initial commit: Azure Document Intelligence Demo"
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy on Streamlit Community Cloud

1. **Go to Streamlit Community Cloud:**
   - Visit https://share.streamlit.io
   - Sign in with your GitHub account

2. **Create a new app:**
   - Click "New app"
   - Select your repository
   - Set branch: `main`
   - Set main file path: `app.py`
   - Click "Deploy"

## Step 3: Configure Secrets

1. **In the Streamlit Cloud dashboard:**
   - Go to your app settings (⚙️ icon)
   - Click "Secrets"
   - Add your Azure credentials in TOML format:

   ```toml
   [azure]
   AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = "https://your-resource.cognitiveservices.azure.com/"
   AZURE_DOCUMENT_INTELLIGENCE_KEY = "your-api-key-here"
   ```

2. **Save the secrets** - your app will automatically restart

## Step 4: Access Your App

Your app will be available at:
```
https://YOUR_USERNAME-YOUR_REPO_NAME.streamlit.app
```

## Getting Azure Credentials

1. Go to Azure Portal (https://portal.azure.com)
2. Create or navigate to your Document Intelligence resource
3. Go to "Keys and Endpoint" section
4. Copy:
   - **Endpoint**: The URL (e.g., `https://your-resource.cognitiveservices.azure.com/`)
   - **Key**: KEY 1 or KEY 2

## Updating Your App

Just push changes to GitHub:
```bash
git add .
git commit -m "Update features"
git push
```

Streamlit will automatically redeploy your app!

## Troubleshooting

### App won't start
- Check that `requirements.txt` includes all dependencies
- Verify secrets are configured correctly in Streamlit settings

### "Not configured" error
- Ensure secrets are in the exact format shown above
- Secret keys are case-sensitive
- No quotes around values in the TOML format

### PDF preview not working
- This is expected on Streamlit Cloud (poppler not available)
- The app will still process PDFs successfully
- Only the preview feature will be unavailable

## Cost

- **Streamlit Community Cloud**: FREE
- **Azure Document Intelligence**: Free tier available (500 pages/month)

## Resources

- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Azure Document Intelligence Pricing](https://azure.microsoft.com/pricing/details/form-recognizer/)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)