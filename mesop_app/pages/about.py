import mesop as me
from components.page_scaffold import page_frame, page_scaffold
from components.header import header

@me.page(
    path="/about",
    title="About - Gemini Enterprise Studio",
)
def page():
    with page_scaffold(page_name="about"):
        with page_frame():
            header("About", "info")
            
            me.markdown("""
# Gemini Enterprise Studio

This platform is a unified demonstration of Google's enterprise-grade AI capabilities.

## 1) Gemini Enterprise API Explorer
Enterprise Conversational Search and API testing allows organizations to search and chat with their own data using Gemini's reasoning capabilities, grounded in private data stores.

## 2) NotebookLM Enterprise API Explorer
Enterprise Notebook Management provides a collaborative environment for analyzing large amounts of information via API. Key features include:
*   **Source Management**: Add PDFs, audio, websites, and YouTube videos.
*   **Enterprise Lifecycle**: Programmatically manage and share notebooks within an organization.
*   **Deep Linking**: Seamlessly transition from custom applications to the full NotebookLM experience.

## Central Config Settings
Configure your Google Cloud environment (Project, Location, Engine ID) centrally within the application settings to use across both explorers.

This application is built with **Mesop**, a Python-based UI framework for building internal tools and AI demos.
""")
