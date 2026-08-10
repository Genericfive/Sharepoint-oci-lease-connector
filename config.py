from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


def required(name: str) -> str:
    value = os.getenv(name, "").strip()

    if not value:
        raise ValueError(
            f"Missing required setting: {name}"
        )

    return value


@dataclass(frozen=True)
class Settings:
    ms_auth_mode: str
    ms_tenant_id: str
    ms_client_id: str
    ms_client_secret: str
    shared_folder_url: str
    token_cache_file: Path
    log_level: str

    @classmethod
    def load(cls):
        load_dotenv()

        ms_auth_mode = os.getenv(
            "MS_AUTH_MODE",
            "device_code"
        ).strip().lower()

        if ms_auth_mode not in {
            "device_code",
            "client_credentials",
        }:
            raise ValueError(
                "MS_AUTH_MODE must be device_code "
                "or client_credentials."
            )

        secret = os.getenv(
            "MS_CLIENT_SECRET",
            ""
        ).strip()

        if (
            ms_auth_mode == "client_credentials"
            and not secret
        ):
            raise ValueError(
                "MS_CLIENT_SECRET is required "
                "for client_credentials."
            )

        return cls(
            ms_auth_mode=ms_auth_mode,
            ms_tenant_id=required(
                "MS_TENANT_ID"
            ),
            ms_client_id=required(
                "MS_CLIENT_ID"
            ),
            ms_client_secret=secret,
            shared_folder_url=required(
                "ONEDRIVE_SHARED_FOLDER_URL"
            ),
            token_cache_file=Path(
                os.getenv(
                    "MS_TOKEN_CACHE_FILE",
                    ".auth/msal_token_cache.json",
                )
            ),
            log_level=os.getenv(
                "LOG_LEVEL",
                "INFO",
            ).strip().upper(),
        )