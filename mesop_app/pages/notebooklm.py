import mesop as me
from components.page_scaffold import page_frame, page_scaffold
from components.header import header
from state.notebooklm_state import NotebookLMState
from services.notebook_client import NotebookClient
from config.default import Default

@me.page(
    path="/notebooklm",
    title="NotebookLM Studio - Enterprise Demo Platform",
)
def page():
    state = me.state(NotebookLMState)
    with page_scaffold(page_name="notebooklm"):
        with page_frame():
            header("NotebookLM Studio", "description")
            
            with me.box(style=me.Style(display="flex", flex_direction="row", gap=24)):
                # Left side: Notebook List & Create
                with me.box(style=me.Style(width=400, display="flex", flex_direction="column", gap=16)):
                    # Config
                    with me.box(style=me.Style(padding=me.Padding.all(16), background=me.theme_var("surface-container-low"), border_radius=12)):
                        me.text("Enterprise Settings", style=me.Style(font_weight="bold", margin=me.Margin(bottom=12)))
                        me.input(label="Project ID", value=state.project_id, on_input=on_project_id_input, style=me.Style(width="100%"))
                        me.select(
                            label="Location",
                            options=[
                                me.SelectOption(label="US", value="us"),
                                me.SelectOption(label="EU", value="eu"),
                            ],
                            value=state.location,
                            on_selection_change=on_location_change,
                            style=me.Style(width="100%"),
                        )
                        me.button("Refresh Notebooks", on_click=on_refresh_notebooks, type="stroked", style=me.Style(width="100%", margin=me.Margin(top=8)))

                    # Create Notebook
                    with me.box(style=me.Style(padding=me.Padding.all(16), background=me.theme_var("surface-container-low"), border_radius=12)):
                        me.text("Create New Notebook", style=me.Style(font_weight="bold", margin=me.Margin(bottom=12)))
                        me.input(label="Notebook Title", value="", on_input=on_new_notebook_title_input, style=me.Style(width="100%"), key="new_notebook_title")
                        me.button("Create", on_click=on_create_notebook, type="raised", style=me.Style(width="100%", margin=me.Margin(top=8)))

                    # Notebook List
                    with me.box(style=me.Style(padding=me.Padding.all(16), background=me.theme_var("surface-container-low"), border_radius=12, flex_grow=1, overflow_y="scroll", max_height=400)):
                        me.text("Your Notebooks", style=me.Style(font_weight="bold", margin=me.Margin(bottom=12)))
                        if state.is_loading:
                            me.progress_spinner()
                        elif not state.notebooks:
                            me.text("No notebooks found.")
                        else:
                            for nb in state.notebooks:
                                is_selected = state.selected_notebook_id == nb.get("id")
                                with me.box(
                                    on_click=lambda e, nb_id=nb.get("id"): on_select_notebook(nb_id),
                                    style=me.Style(
                                        padding=me.Padding.all(12),
                                        margin=me.Margin(bottom=8),
                                        background=me.theme_var("secondary-container") if is_selected else "transparent",
                                        border=me.Border.all(me.BorderSide(width=1, color=me.theme_var("outline-variant"))),
                                        border_radius=8,
                                        cursor="pointer",
                                    )
                                ):
                                    me.text(nb.get("title", "Untitled"), style=me.Style(font_weight="bold"))
                                    me.text(f"ID: {nb.get('id', '')}", style=me.Style(font_size="0.8rem", opacity=0.7))

                # Right side: Details & Source Management
                with me.box(style=me.Style(flex_grow=1, display="flex", flex_direction="column", gap=16)):
                    if not state.selected_notebook_id:
                        with me.box(style=me.Style(display="flex", justify_content="center", align_items="center", height="100%", opacity=0.5)):
                            me.text("Select a notebook to manage sources and sharing")
                    else:
                        selected_nb = next((nb for nb in state.notebooks if nb.get("id") == state.selected_notebook_id), {})
                        
                        # Notebook Actions
                        with me.box(style=me.Style(padding=me.Padding.all(24), background=me.theme_var("surface-container-high"), border_radius=12)):
                            me.text(selected_nb.get("title", "Notebook Details"), type="headline-6")
                            
                            with me.box(style=me.Style(display="flex", gap=16, margin=me.Margin(top=16))):
                                me.button(
                                    "Open in NotebookLM",
                                    on_click=on_open_notebooklm,
                                    type="raised",
                                    icon="open_in_new",
                                )
                                me.button(
                                    "Delete Notebook",
                                    on_click=on_delete_notebook,
                                    type="stroked",
                                    style=me.Style(color=me.theme_var("error")),
                                )

                        # Source Management
                        with me.box(style=me.Style(padding=me.Padding.all(24), background=me.theme_var("surface-container-low"), border_radius=12)):
                            me.text("Add Sources", type="headline-6", style=me.Style(margin=me.Margin(bottom=16)))
                            
                            with me.box(style=me.Style(display="flex", flex_direction="row", gap=16)):
                                # URL Source
                                with me.box(style=me.Style(flex_grow=1)):
                                    me.input(label="Website or YouTube URL", value=state.new_source_url, on_input=on_source_url_input, style=me.Style(width="100%"))
                                    me.button("Add URL", on_click=on_add_url_source, type="stroked", style=me.Style(margin=me.Margin(top=8)))
                                
                                # File Upload
                                with me.box(style=me.Style(flex_grow=1, display="flex", flex_direction="column", align_items="center", justify_content="center", border=me.Border.all(me.BorderSide(width=1, style="dashed", color=me.theme_var("outline"))), border_radius=8)):
                                    me.uploader(
                                        label="Upload PDF/Audio",
                                        on_upload=on_file_upload,
                                        accepted_file_types=["application/pdf", "audio/*"],
                                    )

                        # Sharing
                        with me.box(style=me.Style(padding=me.Padding.all(24), background=me.theme_var("surface-container-low"), border_radius=12)):
                            me.text("Enterprise Sharing", type="headline-6", style=me.Style(margin=me.Margin(bottom=16)))
                            with me.box(style=me.Style(display="flex", gap=16, align_items="center")):
                                me.input(label="Collaborator Email", value=state.share_email, on_input=on_share_email_input, style=me.Style(flex_grow=1))
                                me.select(
                                    label="Role",
                                    options=[
                                        me.SelectOption(label="Reader", value="READER"),
                                        me.SelectOption(label="Writer", value="WRITER"),
                                        me.SelectOption(label="Owner", value="OWNER"),
                                    ],
                                    value=state.share_role,
                                    on_selection_change=on_share_role_change,
                                )
                                me.button("Share", on_click=on_share_notebook, type="raised")

# Event Handlers
def on_project_id_input(e: me.InputEvent):
    me.state(NotebookLMState).project_id = e.value

def on_location_change(e: me.SelectSelectionChangeEvent):
    me.state(NotebookLMState).location = e.value

def on_new_notebook_title_input(e: me.InputEvent):
    # Temporary title storage
    pass

def on_refresh_notebooks(e: me.ClickEvent):
    state = me.state(NotebookLMState)
    state.is_loading = True
    yield
    
    client = NotebookClient(
        project_number=state.project_id or Default.PROJECT_ID,
        location=state.location
    )
    
    try:
        result = client.list_recently_viewed()
        state.notebooks = result.get("notebooks", [])
    except Exception as ex:
        state.error_message = str(ex)
    
    state.is_loading = False
    yield

def on_create_notebook(e: me.ClickEvent):
    # Implementation for creating notebook
    pass

def on_select_notebook(nb_id: str):
    state = me.state(NotebookLMState)
    state.selected_notebook_id = nb_id

def on_open_notebooklm(e: me.ClickEvent):
    state = me.state(NotebookLMState)
    if not state.selected_notebook_id:
        return
        
    client = NotebookClient(
        project_number=state.project_id or Default.PROJECT_ID,
        location=state.location
    )
    url = client.get_notebook_url(state.selected_notebook_id)
    me.navigate(url)

def on_delete_notebook(e: me.ClickEvent):
    # Implementation for deleting notebook
    pass

def on_source_url_input(e: me.InputEvent):
    me.state(NotebookLMState).new_source_url = e.value

def on_add_url_source(e: me.ClickEvent):
    # Implementation for adding URL source
    pass

def on_file_upload(e: me.UploadEvent):
    # Implementation for file upload
    pass

def on_share_email_input(e: me.InputEvent):
    me.state(NotebookLMState).share_email = e.value

def on_share_role_change(e: me.SelectSelectionChangeEvent):
    me.state(NotebookLMState).share_role = e.value

def on_share_notebook(e: me.ClickEvent):
    # Implementation for sharing notebook
    pass
