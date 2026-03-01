import json

from streamlit_js_eval import streamlit_js_eval


def get_browser_location(component_key: str | None = None) -> dict | None:
    if component_key is None:
        component_key = "LOC_PARENT"

    location_str = streamlit_js_eval(
        js_expressions="JSON.stringify(window.parent.location)",
        key=component_key,
    )
    if location_str is not None:
        return json.loads(location_str)

    return None
