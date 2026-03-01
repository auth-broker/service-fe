"""Streamlit App for Auth Broker service frontend."""

from dataclasses import dataclass
from typing import Annotated
from yarl import URL

import streamlit as st
from ab_core.dependency import Depends, inject, sentinel
from streamlit_autorefresh import st_autorefresh

from ab_service.fe.dependencies import AppSettings, BFFClient, get_app_settings, get_bff_client
from ab_service.fe import components as ui
from ab_service.fe.js import get_browser_location, fetch_with_credentials


@dataclass(frozen=True)
class NavLinks:
    login_url: str
    logout_url: str
    refresh_url: str
    me_url: str


@inject
def build_nav_links(
    bff_client: Annotated[BFFClient, Depends(get_bff_client)] = sentinel(),
) -> NavLinks:
    page_location = get_browser_location()

    login_url = (URL(bff_client.base_url) / "auth" / "login")
    logout_url = (URL(bff_client.base_url) / "auth" / "logout")
    refresh_url = (URL(bff_client.base_url) / "auth" / "refresh")
    me_url = (URL(bff_client.base_url) / "auth" / "me")

    if page_location is not None:
        login_url = login_url.with_query(
            return_to=page_location.get("href") if page_location else None
        )
        logout_url = logout_url.with_query(
            return_to=page_location.get("href") if page_location else None
        )
        refresh_url = refresh_url.with_query(
            return_to=page_location.get("href") if page_location else None
        )

    return NavLinks(
        login_url=str(login_url),
        logout_url=str(logout_url),
        refresh_url=str(refresh_url),
        me_url=str(me_url),
    )


# ---- UI sections ----


def render_header() -> None:
    st.title("Auth Broker")
    st.caption(
        "A low-level platform for service-to-service logins powered by captured user OAuth2 sessions "
        "(Playwright / Browserless / CDP), with refresh & retrieval for downstream services."
    )

@inject
def render_sidebar(
    *,
    settings: Annotated[AppSettings, Depends(get_app_settings)] = sentinel(),
    links: NavLinks,
) -> str:
    with st.sidebar:
        st.subheader("Navigation")

        page = st.radio(
            "Go to",
            options=["Landing", "Session", "Settings"],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()
        st.subheader("Auth")
        ui.render_link(links.login_url, link_text="Log in")
        ui.render_link(links.refresh_url, link_text="Refresh session")
        ui.render_link(links.logout_url, link_text="Log out")

        st.divider()
        st.subheader("Diagnostics")

        if st.button("Fetch /auth/me (with cookies)", use_container_width=True):
            st.session_state["do_fetch_me"] = True

        st.divider()
        st.caption("Tip: if you’re testing locally, make sure cookie domains align with your UI/BFF hosts.")

    # Run the fetch outside the sidebar container if you prefer, but it can live here too.
    if st.session_state.get("do_fetch_me"):
        from ab_service.fe.js import fetch_with_credentials

        result = fetch_with_credentials(links.me_url, component_key="FETCH_ME")

        # First run often None; keep the flag set so next rerun receives the value.
        if result is not None:
            st.session_state["do_fetch_me"] = False
            st.session_state["me_result"] = result

    return page


@inject
def render_landing(
    *,
    settings: Annotated[AppSettings, Depends(get_app_settings)] = sentinel(),
) -> None:
    st.header("What this is")
    st.write(
        "Auth Broker is a platform that lets you create **service-to-service logins** using **user access tokens** "
        "captured by monitoring a real user login. It combines tooling like **Playwright**, **Browserless**, and "
        "**Chrome DevTools Protocol (CDP)** to remotely control a browser session, observe OAuth2 flows, "
        "and capture tokens."
    )

    st.write(
        "The platform is deliberately **low-level**: from the UI, you can configure a **Token Issuer** end-to-end "
        "(OAuth2 client config, PKCE vs standard, impersonation strategy, CDP endpoint, timeouts, etc.)."
    )

    st.subheader("High-level flow")
    st.markdown(
        "\n".join(
            [
                "1. You configure a **Token Issuer** (OAuth2 + impersonation tooling).",
                "2. Auth Broker generates a **remote browser GUI URL** (Browserless GUI over CDP).",
                "3. The UI embeds that GUI so you can log in like a normal user.",
                "4. A Playwright/CDP monitor captures the OAuth2 artefacts (code / tokens).",
                "5. Tokens are stored and **refreshed on an interval**.",
                "6. Your downstream services use API keys to retrieve valid access tokens.",
            ]
        )
    )

    st.subheader("What’s in this UI right now")
    st.markdown(
        "\n".join(
            [
                "- Landing page (this page)",
                "- Login / Logout via browser navigation to the BFF",
                "- Manual refresh (browser navigation to the BFF)",
                "- Session “status shell” to plug real context into next",
                "",
                "No raw HTML is used — everything is rendered with Streamlit components.",
            ]
        )
    )


@inject
def render_session(
    *,
    links: NavLinks,
    settings: Annotated[AppSettings, Depends(get_app_settings)] = sentinel(),
) -> None:
    st.header("Session")
    st.write(
        "Because the BFF relies on redirects and browser cookies, **login/logout/refresh happen via browser navigation** "
        "using the buttons in the sidebar."
    )

    st.info(
        "Next step: expose a safe session/context endpoint consumable server-side (or add a small UI-friendly BFF "
        "endpoint that returns session context when cookies are present). Then we can render IdentityContext here."
    )

    st.subheader("Quick checks")
    cols = st.columns(3)
    with cols[0]:
        st.link_button("Log in", links.login_url, use_container_width=True)
    with cols[1]:
        st.link_button("Refresh session", links.refresh_url, use_container_width=True)
    with cols[2]:
        st.link_button("Open /auth/me", links.me_url, use_container_width=True)

    st.divider()

    st.subheader("Automatic refresh (UI rerun helper)")
    st.write(
        "This does **not** perform token refresh via fetch. Instead, it keeps the UI rerunning on an interval, "
        "so you can pair it with periodic browser refresh navigations while developing."
    )

    if settings.AUTO_REFRESH_ENABLED:
        st_autorefresh(interval=settings.AUTO_REFRESH_SECONDS * 1000, key="ui_autorefresh")
        st.caption(f"UI auto-rerun is enabled every {settings.AUTO_REFRESH_SECONDS} seconds.")
    else:
        st.caption("UI auto-rerun is disabled.")


@inject
def render_settings(
    *,
    settings: Annotated[AppSettings, Depends(get_app_settings)] = sentinel(),
    bff_client: Annotated[BFFClient, Depends(get_bff_client)] = sentinel(),
) -> None:
    st.header("Settings")
    st.write("These are loaded via **pydantic-settings** (environment variables).")

    st.subheader("Current configuration")
    st.json(
        {
            "BFF_SERVICE_BASE_URL": bff_client.base_url,
            "AUTO_REFRESH_ENABLED": settings.AUTO_REFRESH_ENABLED,
            "AUTO_REFRESH_SECONDS": settings.AUTO_REFRESH_SECONDS,
        }
    )


# ---- main ----


def app() -> None:
    st.set_page_config(
        page_title="Auth Broker",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    settings = AppSettings()
    links = build_nav_links()

    render_header()
    page = render_sidebar(links=links)

    if page == "Landing":
        render_landing()
    elif page == "Session":
        render_session(links=links)
    else:
        render_settings()


if __name__ == "__main__":
    app()
