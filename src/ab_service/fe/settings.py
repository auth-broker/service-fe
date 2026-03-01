"""Settings for the Streamlit UI."""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Streamlit UI settings.

    Note:
      - BFF fetch base_url is loaded via your custom DI into the BFFClient.
      - BUT browser navigation still needs a PUBLIC BFF base URL so the user's browser
        can follow redirects and set cookies correctly.

    """

    # Auto-refresh behaviour (for browser refresh navigation prompts + UI reruns)
    AUTO_REFRESH_ENABLED: bool = True
    AUTO_REFRESH_SECONDS: int = 50  # keep under typical access token expiry windows
