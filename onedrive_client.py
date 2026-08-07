import base64
from pathlib import PurePosixPath
from urllib.parse import quote

import requests

from models import RemoteFile


GRAPH = "https://graph.microsoft.com/v1.0"


class OneDriveReadOnlyClient:
    def __init__(self, access_token: str, shared_folder_url: str):
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {access_token}"
        self.shared_folder_url = shared_folder_url

        self.root_item = self._resolve_shared_folder()

        parent = self.root_item.get("parentReference", {})
        self.drive_id = parent.get("driveId")

        if not self.drive_id:
            raise RuntimeError(
                "Could not determine the shared folder drive ID."
            )

        self.root_name = self.root_item.get("name", "shared-folder")

    @staticmethod
    def _share_token(url: str) -> str:
        token = base64.urlsafe_b64encode(
            url.encode("utf-8")
        ).decode("ascii")

        return "u!" + token.rstrip("=")

    def _get(self, url: str, stream: bool = False):
        response = self.session.get(
            url,
            timeout=300,
            stream=stream,
            allow_redirects=True,
        )

        response.raise_for_status()
        return response

    def _get_json(self, url: str) -> dict:
        return self._get(url).json()

    def _resolve_shared_folder(self) -> dict:
        token = self._share_token(self.shared_folder_url)

        url = (
            f"{GRAPH}/shares/"
            f"{quote(token, safe='!')}/driveItem"
        )

        response = self.session.get(
            url,
            headers={
                "Authorization": self.session.headers["Authorization"],
                "Prefer": "redeemSharingLinkIfNecessary",
            },
            timeout=300,
        )

        if not response.ok:
            raise RuntimeError(
                f"Microsoft Graph error {response.status_code}: {response.text}"
            )

        item = response.json()

        if "folder" not in item:
            raise RuntimeError(
                "The supplied OneDrive link did not resolve to a folder."
            )

        return item

    def iter_files(self):
        yield from self._walk(
            self.root_item["id"],
            PurePosixPath(self.root_name),
        )

    def _walk(
        self,
        folder_id: str,
        current_path: PurePosixPath,
    ):
        url = (
            f"{GRAPH}/drives/{quote(self.drive_id)}/items/"
            f"{quote(folder_id)}/children?$top=200"
        )

        while url:
            payload = self._get_json(url)

            for item in payload.get("value", []):
                name = item.get("name", "unnamed")
                path = current_path / name

                if "folder" in item:
                    yield from self._walk(
                        item["id"],
                        path,
                    )

                elif "file" in item:
                    yield RemoteFile(
                        item_id=item["id"],
                        name=name,
                        relative_path=str(path).replace("\\", "/"),
                        size=int(item.get("size", 0)),
                        modified_at=item.get(
                            "lastModifiedDateTime",
                            "",
                        ),
                        etag=item.get("eTag", ""),
                        mime_type=item.get(
                            "file",
                            {},
                        ).get(
                            "mimeType",
                            "application/octet-stream",
                        ),
                    )

            url = payload.get("@odata.nextLink")

    def open_content_stream(self, item_id: str):
        url = (
            f"{GRAPH}/drives/{quote(self.drive_id)}/items/"
            f"{quote(item_id)}/content"
        )

        response = self._get(
            url,
            stream=True,
        )

        response.raw.decode_content = True
        return response