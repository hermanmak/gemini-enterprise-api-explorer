import mesop as me
from dataclasses import field
from typing import List, Optional
from common.models.schemas import SearchResult

@me.stateclass
class GeminiState:
    project_id: str = ""
    location: str = "global"
    data_store_id: str = ""
    input: str = ""
    output: str = ""
    chat_history: List[dict] = field(default_factory=list)
    is_loading: bool = False
    search_results: List[SearchResult] = field(default_factory=list)
    error_message: str = ""
