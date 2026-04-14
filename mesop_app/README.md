# Gemini Enterprise Studio - Mesop UI

This directory contains a modern, Python-only UI for the Gemini Enterprise Studio, built using **Mesop**.

## Why Mesop?

- **Python-only**: No JavaScript/TypeScript/CSS knowledge required to build complex UIs.
- **Fast Development**: Rapidly prototype and build internal tools or AI demos.
- **Integrated State**: Built-in reactive state management.
- **Google Design Language**: Uses standard Google UI components and styling.

## Project Structure

- `main.py`: The entry point for the FastAPI server hosting Mesop.
- `pages/`: Individual page definitions (Home, Gemini, NotebookLM, etc.).
- `components/`: Reusable UI components (Header, SideNav, PageScaffold).
- `services/`: Backend API clients for Gemini and NotebookLM.
- `state/`: Application and page-level state definitions.
- `config/`: Configuration files and navigation structure.

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Authentication

Ensure you have Application Default Credentials (ADC) set up:

```bash
gcloud auth application-default login
```

### 3. Run the Application

```bash
python main.py
```

Open your browser to [http://localhost:8080/home](http://localhost:8080/home).

## Features

- **Gemini Explorer**: Enterprise Conversational Search with streaming chat and grounded citations.
- **NotebookLM Studio**: Manage enterprise notebooks, upload sources (PDF, Audio, Web, YouTube), and share with collaborators.
- **Unified Configuration**: Easily toggle between Google Cloud projects and regional locations.
- **Theming**: Support for both Light and Dark modes.
