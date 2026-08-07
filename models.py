from dataclasses import dataclass


@dataclass(frozen=True)
class RemoteFile:
    item_id: str
    name: str
    relative_path: str
    size: int
    modified_at: str
    etag: str
    mime_type: str
