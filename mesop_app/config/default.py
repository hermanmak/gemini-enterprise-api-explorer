import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)


class NavItem(BaseModel):
    id: int
    display: str
    icon: str
    route: Optional[str] = None
    group: Optional[str] = None
    align: Optional[str] = None
    feature_flag: Optional[str] = None
    feature_flag_not: Optional[str] = None
    description: Optional[str] = None


class NavConfig(BaseModel):
    pages: List[NavItem]


@dataclass
class Default:
    """Defaults class"""

    VERSION: str = "1.0.0"
    APP_ENV: str = os.environ.get("APP_ENV", "local")
    PROJECT_ID: str = os.environ.get("PROJECT_ID", "")
    LOCATION: str = os.environ.get("LOCATION", "us-central1")
    GA_MEASUREMENT_ID: str = os.environ.get("GA_MEASUREMENT_ID")

    # Gemini Enterprise
    GEMINI_LOCATION: str = os.environ.get("GEMINI_LOCATION", "global")
    
    # NotebookLM
    NOTEBOOKLM_LOCATION: str = os.environ.get("NOTEBOOKLM_LOCATION", "us")


def get_config_path(rel_path: str) -> str:
    """Returns the path to a configuration file."""
    # Base directory of the mesop_app
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, rel_path)


def get_welcome_page_config():
    path = get_config_path("config/navigation.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)

    config = NavConfig(**data)

    def is_feature_enabled(page: NavItem):
        if page.feature_flag:
            return bool(getattr(Default, page.feature_flag, False))
        if page.feature_flag_not:
            return not bool(getattr(Default, page.feature_flag_not, False))
        return True

    filtered_pages = [
        page.model_dump(exclude_none=True)
        for page in config.pages
        if is_feature_enabled(page)
    ]

    return sorted(filtered_pages, key=lambda x: x["id"])
