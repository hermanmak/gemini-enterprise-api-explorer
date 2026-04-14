import mesop as me
from components.svg_icon.svg_icon import svg_icon

# List of custom icons that should use the svg_icon component.
# These match the set of icons used throughout the app in sidebars and headers.
CUSTOM_ICONS = ["spark", "style", "scene", "banana"]


def render_icon(icon_name: str):
    """Renders a custom SVG icon if it's in the CUSTOM_ICONS list, otherwise renders a standard me.icon."""
    if icon_name in CUSTOM_ICONS:
        with me.box(style=me.Style(width=24, height=24)):
            svg_icon(icon_name=icon_name)
    else:
        me.icon(icon=icon_name)
