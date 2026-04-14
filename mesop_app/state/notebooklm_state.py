import mesop as me
from dataclasses import field
from typing import List, Optional, Any

@me.stateclass
class NotebookLMState:
    project_id: str = ""
    location: str = "us"
    notebooks: List[dict] = field(default_factory=list)
    selected_notebook_id: str = ""
    is_loading: bool = False
    error_message: str = ""
    
    # Source management
    new_source_url: str = ""
    upload_file_path: str = ""
    
    # Sharing
    share_email: str = ""
    share_role: str = "READER"
