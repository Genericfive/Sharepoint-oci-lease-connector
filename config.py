from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required setting: {name}")
    return value


def as_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    ms_auth_mode: str
    ms_tenant_id: str
    ms_client_id: str
    ms_client_secret: str
    shared_folder_url: str
    token_cache_file: Path
    oci_auth_mode: str
    oci_config_file: str
    oci_config_profile: str
    oci_namespace: str
    oci_bucket_name: str
    oci_object_prefix: str
    mode: str
    skip_unchanged: bool
    max_files: int
    log_level: str

    @classmethod
    def load(cls):
        load_dotenv()

        mode = os.getenv("MODE", "list").strip().lower()
        if mode not in {"list", "sync"}:
            raise ValueError("MODE must be list or sync.")

        ms_auth_mode = os.getenv("MS_AUTH_MODE", "device_code").strip().lower()
        if ms_auth_mode not in {"device_code", "client_credentials"}:
            raise ValueError("MS_AUTH_MODE must be device_code or client_credentials.")

        oci_auth_mode = os.getenv("OCI_AUTH_MODE", "config_file").strip().lower()
        if oci_auth_mode not in {"config_file", "resource_principal"}:
            raise ValueError("OCI_AUTH_MODE must be config_file or resource_principal.")

        try:
            max_files = int(os.getenv("MAX_FILES", "0"))
        except ValueError as exc:
            raise ValueError("MAX_FILES must be an integer.") from exc

        secret = os.getenv("MS_CLIENT_SECRET", "").strip()
        if ms_auth_mode == "client_credentials" and not secret:
            raise ValueError("MS_CLIENT_SECRET is required for client_credentials.")

        return cls(
            ms_auth_mode=ms_auth_mode,
            ms_tenant_id=required("MS_TENANT_ID"),
            ms_client_id=required("MS_CLIENT_ID"),
            ms_client_secret=secret,
            shared_folder_url=required("ONEDRIVE_SHARED_FOLDER_URL"),
            token_cache_file=Path(os.getenv("MS_TOKEN_CACHE_FILE", ".auth/msal_token_cache.json")),
            oci_auth_mode=oci_auth_mode,
            oci_config_file=os.getenv("OCI_CONFIG_FILE", str(Path.home() / ".oci" / "config")).strip(),
            oci_config_profile=os.getenv("OCI_CONFIG_PROFILE", "DEFAULT").strip(),
            oci_namespace=required("OCI_NAMESPACE"),
            oci_bucket_name=required("OCI_BUCKET_NAME"),
            oci_object_prefix=os.getenv("OCI_OBJECT_PREFIX", "inbound/onedrive").strip().strip("/"),
            mode=mode,
            skip_unchanged=as_bool("SKIP_UNCHANGED", True),
            max_files=max_files,
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        )
