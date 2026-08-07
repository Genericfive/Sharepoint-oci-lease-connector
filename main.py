import logging
import sys

from config import Settings
from microsoft_auth import MicrosoftTokenProvider
from onedrive_client import OneDriveReadOnlyClient
from oci_storage import OCIStorage
from sync_service import SyncService


def main() -> int:
    try:
        settings = Settings.load()
        logging.basicConfig(
            level=getattr(logging, settings.log_level, logging.INFO),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

        token = MicrosoftTokenProvider(
            settings.ms_auth_mode,
            settings.ms_tenant_id,
            settings.ms_client_id,
            settings.ms_client_secret,
            settings.token_cache_file,
        ).get_access_token()

        onedrive = OneDriveReadOnlyClient(
            token,
            settings.shared_folder_url,
        )

        storage = OCIStorage(
            settings.oci_auth_mode,
            settings.oci_config_file,
            settings.oci_config_profile,
            settings.oci_namespace,
            settings.oci_bucket_name,
            settings.oci_object_prefix,
        )

        totals = SyncService(
            onedrive,
            storage,
            settings.mode,
            settings.skip_unchanged,
            settings.max_files,
        ).run()

        print("Completed:", totals)
        return 0

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
