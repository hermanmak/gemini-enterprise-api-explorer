import mesop as me
from components.page_scaffold import page_frame, page_scaffold
from components.header import header
from state.state import AppState
from config.default import Default

@me.page(
    path="/config",
    title="Central Config Settings - Gemini Enterprise Studio",
)
def page():
    state = me.state(AppState)
    with page_scaffold(page_name="config"):
        with page_frame():
            header("Central Config Settings", "settings")
            
            with me.box(style=me.Style(display="flex", flex_direction="column", gap=24, max_width=600, margin=me.Margin(top=24))):
                with me.box(style=me.Style(padding=me.Padding.all(24), background=me.theme_var("surface-container-low"), border_radius=12)):
                    me.text("General Configuration", type="headline-6", style=me.Style(margin=me.Margin(bottom=16)))
                    
                    me.input(
                        label="Project ID",
                        value=state.project_id or Default.PROJECT_ID,
                        on_input=on_project_id_input,
                        style=me.Style(width="100%"),
                    )
                    
                    me.select(
                        label="Default Location",
                        options=[
                            me.SelectOption(label="US", value="us"),
                            me.SelectOption(label="EU", value="eu"),
                            me.SelectOption(label="Global", value="global"),
                        ],
                        value=state.location or Default.LOCATION,
                        on_selection_change=on_location_change,
                        style=me.Style(width="100%"),
                    )

                with me.box(style=me.Style(padding=me.Padding.all(24), background=me.theme_var("surface-container-low"), border_radius=12)):
                    me.text("Appearance", type="headline-6", style=me.Style(margin=me.Margin(bottom=16)))
                    me.button(
                        f"Switch to {'Dark' if me.theme_brightness() == 'light' else 'Light'} Mode",
                        on_click=on_toggle_theme,
                        type="stroked",
                    )

def on_project_id_input(e: me.InputEvent):
    me.state(AppState).project_id = e.value

def on_location_change(e: me.SelectSelectionChangeEvent):
    me.state(AppState).location = e.value

def on_toggle_theme(e: me.ClickEvent):
    state = me.state(AppState)
    new_mode = "dark" if me.theme_brightness() == "light" else "light"
    me.set_theme_mode(new_mode)
    state.theme_mode = new_mode
