# Gemini Enterprise Studio

This application demonstrates the feasibility of interacting with **Gemini Enterprise Studio** (previously known as **GenMedia Studio**) and **NotebookLM Enterprise** functionality via API. This is helpful to prove that subscribers can integrate these capabilities into their own applications, services, and UI.

## Use Cases

**Gemini Enterprise**: Use as an **agent hub** and integrate agents into your own app, without redirecting users to the Gemini Enterprise interface.

**NotebookLM Enterprise**: **Create** and **manage** notebooks programmatically, add data sources (text, web, YouTube, Google Drive, files), and share with team members. 
> **Note:**  There is currently no programmatic support for querying (e.g. ask questions)  NotebookLM.

> **Note:** This explorer app demonstrates API integration using **Application Default Credentials (ADC)**, not user OAuth credentials. For production applications serving end users, you would typically implement OAuth 2.0 for user authentication.

## Prerequisites

Before running the application, ensure you have:

- **Python 3.9+**
- **Node.js 18+** and npm
- **Google Cloud Project** with Discovery Engine API enabled (The project where Gemini Enterprise is enabled). Ensure you have license and access to that Gemini Enterprise instance
- **Application Default Credentials (ADC)** configured 

### Setting up Application Default Credentials

This application requires ADC to authenticate with Google Cloud APIs:

```bash
# Install Google Cloud SDK (if not already installed)
brew install google-cloud-sdk  # macOS
# Or download from: https://cloud.google.com/sdk/docs/install

# Authenticate and set up ADC
gcloud auth application-default login

# For NotebookLM with Google Drive access (optional)
gcloud auth login --enable-gdrive-access

# Verify authentication
gcloud auth application-default print-access-token
```

> **Important:** Ensure you have the necessary permissions in your Google Cloud project to access Discovery Engine APIs and NotebookLM Enterprise.

## 🚀 Quick Start (Next.js + FastAPI)

```bash
git clone https://github.com/0nri/gemini-enterprise-api-explorer.git
cd gemini-enterprise-api-explorer
chmod +x setup.sh
./setup.sh
```

The script will:

- ✅ Check prerequisites (Python 3.9+, Node.js 18+)
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Start both backend and frontend servers
- ✅ Open your browser to http://localhost:3000

## 🎨 Mesop-based UI (Alternative)

We also provide a modern, Python-only UI built with **Mesop**. This is the recommended interface for quick demos and internal tools.

### Running the Mesop App (Recommended)

To set up and run the Mesop application:

```bash
chmod +x setup-mesop.sh start-mesop.sh
./setup-mesop.sh
./start-mesop.sh
```

- ✅ Automatically creates a unified virtual environment in `.venv`.
- ✅ Installs all necessary dependencies.
- ✅ Start the server on http://localhost:8080/home.

### Configuration (Mesop)

- The Mesop app uses the same **Project Number**, **Engine ID**, and **Location** as the Next.js version.
- You can configure these in the **Settings** page within the app.

**Then configure your credentials in the sidebar:**

- Enter your Google Cloud **Project Number** (not project ID)
- Enter your Agentspace **Engine ID**
- Click "Apply Configuration"
- Start exploring!

### Finding Your Configuration Values

- **Project Number**: Google Cloud Console → Project Settings → Project number
- **Engine ID**: Discovery Engine → Engines → Your engine name
- **Location**: Usually `us`, `eu`, or `global` (default: `us`)

## Features

### 1) Gemini Enterprise API Explorer

- **Gemini Enterprise Studio** - Test various Gemini Enterprise API endpoints
- **Chat Interface** - Interactive chat with Gemini Enterprise agents (available in both Next.js and Mesop UIs)
- **Search** - Enterprise search functionality
- **Agent Management** - List and manage available agents

### 2) NotebookLM Enterprise API Explorer

- **Notebook Management** - Create, list, share, and delete notebooks
- **Multi-format Sources** - Add text, web URLs, YouTube videos, Google Drive docs, and files
- **Collaboration** - Share notebooks with team members
- **Source Organization** - Manage and organize notebook data sources
- **Deep Linking** - Transition seamlessly to the full NotebookLM UI

### Central Config Settings

Both the Next.js and Mesop interfaces provide a central configuration section to manage your Google Cloud environment:
- **Project Number**: Set your target Google Cloud Project Number.
- **Location**: Configure regional locations (e.g., `us`, `eu`, `global`).
- **Engine ID**: Specify the Discovery Engine ID for Gemini Enterprise features.
- **Config Persistence**: Settings are saved locally for ease of use.

## 📚 Documentation

- **[NotebookLM Guide](docs/NOTEBOOKLM.md)** - Complete NotebookLM features and API reference
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture and development guide
- **[Mesop Architecture](mesop_app/README.md)** - Guide for the Python-only Mesop UI
- **[API Reference](http://localhost:8000/docs)** - Interactive API docs (when backend is running)

## 🐛 Troubleshooting

### Authentication Issues

```bash
# Re-authenticate
gcloud auth application-default login

# Verify
gcloud auth application-default print-access-token
```
