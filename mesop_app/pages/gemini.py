import mesop as me
import asyncio
from components.page_scaffold import page_frame, page_scaffold
from components.header import header
from state.gemini_state import GeminiState
from services.conversation_client import ConversationClient
from config.default import Default

@me.page(
    path="/gemini",
    title="Gemini Explorer - Enterprise Demo Platform",
)
def page():
    state = me.state(GeminiState)
    with page_scaffold(page_name="gemini"):
        with page_frame():
            header("Gemini Explorer", "spark")
            
            with me.box(style=me.Style(display="flex", flex_direction="row", gap=24, height="calc(100vh - 200px)")):
                # Left side: Chat
                with me.box(style=me.Style(flex_grow=1, display="flex", flex_direction="column", gap=16)):
                    # Chat history area
                    with me.box(
                        style=me.Style(
                            flex_grow=1,
                            overflow_y="scroll",
                            padding=me.Padding.all(16),
                            background=me.theme_var("surface-container-lowest"),
                            border_radius=12,
                            display="flex",
                            flex_direction="column",
                            gap=12,
                        )
                    ):
                        if not state.chat_history:
                            with me.box(style=me.Style(display="flex", justify_content="center", align_items="center", height="100%", opacity=0.5)):
                                me.text("Start a conversation with Gemini Enterprise")
                        
                        for msg in state.chat_history:
                            is_user = msg["role"] == "user"
                            with me.box(
                                style=me.Style(
                                    align_self="flex-end" if is_user else "flex-start",
                                    background=me.theme_var("primary-container") if is_user else me.theme_var("secondary-container"),
                                    color=me.theme_var("on-primary-container") if is_user else me.theme_var("on-secondary-container"),
                                    padding=me.Padding.all(12),
                                    border_radius=12,
                                    max_width="80%",
                                )
                            ):
                                me.markdown(msg["content"])

                    # Input area
                    with me.box(style=me.Style(display="flex", flex_direction="row", gap=8, align_items="center")):
                        me.textarea(
                            label="Query",
                            value=state.input,
                            on_input=on_input,
                            style=me.Style(flex_grow=1),
                            rows=3,
                        )
                        with me.content_button(
                            type="raised",
                            on_click=on_submit,
                            disabled=state.is_loading or not state.input,
                        ):
                            if state.is_loading:
                                me.progress_spinner(diameter=20)
                            else:
                                me.icon(icon="send")

                # Right side: Configuration & Results
                with me.box(style=me.Style(width=300, display="flex", flex_direction="column", gap=16)):
                    with me.box(
                        style=me.Style(
                            padding=me.Padding.all(16),
                            background=me.theme_var("surface-container-low"),
                            border_radius=12,
                        )
                    ):
                        me.text("Configuration", style=me.Style(font_weight="bold", margin=me.Margin(bottom=12)))
                        me.input(label="Project ID", value=state.project_id, on_input=on_project_id_input, style=me.Style(width="100%"))
                        me.input(label="Data Store ID", value=state.data_store_id, on_input=on_data_store_id_input, style=me.Style(width="100%"))
                        me.select(
                            label="Location",
                            options=[
                                me.SelectOption(label="Global", value="global"),
                                me.SelectOption(label="US", value="us"),
                                me.SelectOption(label="EU", value="eu"),
                            ],
                            value=state.location,
                            on_selection_change=on_location_change,
                            style=me.Style(width="100%"),
                        )

                    if state.search_results:
                        with me.box(
                            style=me.Style(
                                padding=me.Padding.all(16),
                                background=me.theme_var("surface-container-low"),
                                border_radius=12,
                                flex_grow=1,
                                overflow_y="scroll",
                            )
                        ):
                            me.text("Grounded Sources", style=me.Style(font_weight="bold", margin=me.Margin(bottom=12)))
                            for res in state.search_results:
                                with me.box(style=me.Style(margin=me.Margin(bottom=8), padding=me.Padding.all(8), border=me.Border.all(me.BorderSide(width=1, color=me.theme_var("outline-variant"))), border_radius=8)):
                                    me.text(res.get("title", "Untitled Document"), style=me.Style(font_size="0.9rem", font_weight="bold"))
                                    me.text(f"ID: {res.get('id', 'N/A')}", style=me.Style(font_size="0.8rem", opacity=0.7))

def on_input(e: me.InputEvent):
    state = me.state(GeminiState)
    state.input = e.value

def on_project_id_input(e: me.InputEvent):
    state = me.state(GeminiState)
    state.project_id = e.value

def on_data_store_id_input(e: me.InputEvent):
    state = me.state(GeminiState)
    state.data_store_id = e.value

def on_location_change(e: me.SelectSelectionChangeEvent):
    state = me.state(GeminiState)
    state.location = e.value

def on_submit(e: me.ClickEvent):
    state = me.state(GeminiState)
    if not state.input:
        return

    query = state.input
    state.chat_history.append({"role": "user", "content": query})
    state.input = ""
    state.is_loading = True
    state.search_results = []
    yield
    
    # We'll call the client here.
    # Note: Mesop handlers can be generators (yield).
    # Since we need to call an async client, we'll use a helper.
    
    client = ConversationClient(
        project_number=state.project_id or Default.PROJECT_ID,
        location=state.location,
        engine_id=state.data_store_id
    )
    
    try:
        # For simplicity in this demo, we'll collect the full response
        # but the client supports streaming.
        
        # We need an event loop to run the async generator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        full_text = ""
        
        async def run_query():
            nonlocal full_text
            async for chunk in client.converse_stream(query):
                if "text" in chunk:
                    full_text += chunk["text"]
                if "search_results" in chunk:
                    state.search_results.extend(chunk["search_results"])
                if "error" in chunk:
                    state.error_message = chunk["error"]
        
        loop.run_until_complete(run_query())
        
        if full_text:
            state.chat_history.append({"role": "assistant", "content": full_text})
        elif state.error_message:
            state.chat_history.append({"role": "assistant", "content": f"Error: {state.error_message}"})
            
    except Exception as ex:
        state.error_message = str(ex)
        state.chat_history.append({"role": "assistant", "content": f"System Error: {str(ex)}"})
    
    state.is_loading = False
    yield
