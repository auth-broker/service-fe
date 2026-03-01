"""Settings for the Streamlit UI."""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Streamlit UI settings."""

    # Auto-refresh behaviour (for browser refresh navigation prompts + UI reruns)
    AUTO_REFRESH_ENABLED: bool = True
    AUTO_REFRESH_SECONDS: int = 50  # keep under typical access token expiry windows
