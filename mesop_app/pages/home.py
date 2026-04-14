import mesop as me
from components.page_scaffold import page_frame, page_scaffold
from components.header import header
from components.icon import render_icon
from config.default import get_welcome_page_config
from state.state import AppState

@me.page(
    path="/home",
    title="Gemini Enterprise Studio",
    security_policy=me.SecurityPolicy(
        dangerously_disable_trusted_types=True,
    ),
)
def page():
    """Main Home Page."""
    state = me.state(AppState)
    with page_scaffold(page_name="home"):
        with page_frame():
            home_page_content(state)

def home_page_content(state: AppState):
    with me.box(
        style=me.Style(
            background=me.theme_var("background"),
            display="flex",
            flex_direction="column",
        )
    ):
        header("Gemini Enterprise Studio", "spark")
        
        me.text(
            "Welcome to the Gemini Enterprise Studio featuring:",
            style=me.Style(
                font_size="1.5rem",
                margin=me.Margin(top=24, bottom=12),
                color=me.theme_var("on-surface"),
            ),
        )
        
        me.text(
            "1) Gemini Enterprise API Explorer\n2) NotebookLM Enterprise API Explorer",
            style=me.Style(
                font_size="1.1rem",
                margin=me.Margin(bottom=24),
                color=me.theme_var("on-surface-variant"),
            ),
        )

        me.text(
            "Select a section from the sidebar or click a card below, and ensure you've set your Central Config Settings.",
        )

        with me.box(
            style=me.Style(
                display="flex",
                flex_direction="row",
                flex_wrap="wrap",
                gap=16,
                margin=me.Margin(top=24),
            )
        ):
            pages = get_welcome_page_config()
            for page_data in pages:
                if page_data.get("route") == "/home":
                    continue
                
                with me.box(
                    on_click=lambda e, r=page_data.get("route"): me.navigate(r),
                    style=me.Style(
                        background=me.theme_var("secondary-container"),
                        color=me.theme_var("on-secondary-container"),
                        padding=me.Padding.all(24),
                        border_radius=12,
                        width=300,
                        cursor="pointer",
                        display="flex",
                        flex_direction="column",
                        gap=8,
                    )
                ):
                    with me.box(style=me.Style(display="flex", align_items="center", gap=8)):
                        render_icon(page_data.get("icon", "arrow_forward"))
                        me.text(
                            page_data.get("display", ""),
                            style=me.Style(font_size="1.2rem", font_weight="bold"),
                        )
                    me.text(
                        page_data.get("description", ""),
                        style=me.Style(font_size="0.9rem"),
                    )
