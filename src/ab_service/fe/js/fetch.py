import json
from streamlit_js_eval import streamlit_js_eval

def fetch_with_credentials(url: str, *, component_key: str) -> dict | None:
    """
    Browser-side fetch(url, {credentials:'include'}) and return JSON (or text/error).
    Returns None on first run (component round-trip), like other streamlit_js_eval calls.
    """
    js = f"""
    (async () => {{
      try {{
        const res = await fetch({json.dumps(url)}, {{
          method: "GET",
          credentials: "include",
          headers: {{
            "Accept": "application/json"
          }},
        }});

        const contentType = res.headers.get("content-type") || "";
        const body = contentType.includes("application/json")
          ? await res.json()
          : await res.text();

        return JSON.stringify({{
          ok: res.ok,
          status: res.status,
          statusText: res.statusText,
          url: res.url,
          body
        }});
      }} catch (e) {{
        return JSON.stringify({{
          ok: false,
          status: 0,
          statusText: "FETCH_ERROR",
          url: {json.dumps(url)},
          body: String(e)
        }});
      }}
    }})()
    """

    out = streamlit_js_eval(js_expressions=js, key=component_key)
    if out:
        return json.loads(out)
    return None
