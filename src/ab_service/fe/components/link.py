import streamlit as st


def render_link(
    url: str,
    link_text: str,
) -> None:
    st.markdown(
        f"""
         <a href="{url}" target="_self">{link_text}</a>
         """,
        unsafe_allow_html=True,
    )
