from __future__ import annotations

import sys

from config import Settings
from microsoft_auth import MicrosoftAuthenticator
from onedrive_client import OneDriveReadOnlyClient


def main() -> None:
    print("=" * 80)
    print("SHAREPOINT LEASE BROWSER")
    print("=" * 80)

    settings = Settings.load()

    authenticator = MicrosoftAuthenticator(
        tenant_id=settings.ms_tenant_id,
        client_id=settings.ms_client_id,
    )

    token = authenticator.get_access_token()

    sharepoint = OneDriveReadOnlyClient(
        access_token=token,
        shared_folder_url=settings.shared_folder_url,
    )

    print("\nReading SharePoint folders and files...")
    print("SharePoint is the source of the lease documents.\n")

    files = list(sharepoint.iter_files())

    if not files:
        print("No files found.")
        return

    for index, file in enumerate(files, start=1):
        print(f"{index:04d} | {file.relative_path}")

    print("\n" + "=" * 80)
    print(f"Files found: {len(files)}")
    print("=" * 80)

    while True:
        choice = input(
            "\nSelect file number (or Q to quit): "
        ).strip()

        if choice.lower() == "q":
            print("Cancelled.")
            return

        try:
            selected_number = int(choice)

            if not 1 <= selected_number <= len(files):
                print(
                    f"Enter a number between 1 and {len(files)}."
                )
                continue

            break

        except ValueError:
            print("Enter a valid file number.")

    selected_file = files[selected_number - 1]

    print("\nSelected document")
    print("=" * 80)
    print(f"Name: {selected_file.name}")
    print(f"Path: {selected_file.relative_path}")
    print(f"Size: {selected_file.size:,} bytes")
    print("=" * 80)

    print("\nReading selected document from SharePoint...")
    print("No local lease file will be created.")

    response = sharepoint.open_content_stream(
        selected_file.item_id
    )

    try:
        document_bytes = response.content

        print("\nSUCCESS")
        print("=" * 80)
        print(f"File: {selected_file.name}")
        print(f"Bytes loaded: {len(document_bytes):,}")
        print("Document is currently held in memory only.")
        print("No local PDF was created.")
        print("=" * 80)

        # Later this will be passed to Lease-AI.
        #
        # Example:
        #
        # process_lease(
        #     document_bytes,
        #     selected_file.name
        # )

    finally:
        response.close()

    del document_bytes

    print("\nIn-memory document test completed.")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    except Exception as exc:
        print("\nCONNECTOR FAILED")
        print(f"{type(exc).__name__}: {exc}")
        raise