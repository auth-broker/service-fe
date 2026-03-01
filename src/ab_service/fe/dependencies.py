"""This module defines the dependencies for the service, such as configuration settings and clients for external services."""

from collections.abc import Generator
from typing import Annotated

from ab_client.bff import SyncClient as BFFClient
from ab_core.dependency import Depends, inject
from ab_core.dependency.loaders.environment_object import ObjectLoaderEnvironment

from .settings import AppSettings


@inject
def get_app_settings(
    _app_settings: Annotated[
        AppSettings,
        Depends(
            ObjectLoaderEnvironment[AppSettings](env_prefix=""),
            persist=True,
        ),
    ],
) -> Generator[AppSettings, None, None]:
    yield _app_settings


@inject
def get_bff_client(
    _bff_client: Annotated[
        BFFClient,
        Depends(
            ObjectLoaderEnvironment[BFFClient](env_prefix="BFF_SERVICE"),
            persist=True,
        ),
    ],
) -> Generator[BFFClient, None, None]:
    yield _bff_client


__all__ = [
    BFFClient,
    get_bff_client,
    AppSettings,
    get_app_settings,
]
