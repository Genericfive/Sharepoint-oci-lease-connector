from datetime import datetime, timezone
import logging

LOGGER = logging.getLogger(__name__)


class SyncService:
    def __init__(self, onedrive, storage, mode, skip_unchanged, max_files):
        self.onedrive = onedrive
        self.storage = storage
        self.mode = mode
        self.skip_unchanged = skip_unchanged
        self.max_files = max_files

    @staticmethod
    def signature(remote):
        return {
            "etag": remote.etag,
            "size": remote.size,
            "modified_at": remote.modified_at,
            "source_path": remote.relative_path,
        }

    def run(self):
        state = self.storage.load_state()
        known = state.setdefault("files", {})
        totals = {"seen": 0, "uploaded": 0, "skipped": 0, "listed": 0, "failed": 0}

        for remote in self.onedrive.iter_files():
            if self.max_files and totals["seen"] >= self.max_files:
                break
            totals["seen"] += 1

            current = self.signature(remote)
            previous = known.get(remote.item_id)

            if self.mode == "list":
                print(
                    f"{remote.relative_path} | {remote.size} bytes | "
                    f"{remote.modified_at}"
                )
                totals["listed"] += 1
                continue

            if self.skip_unchanged and previous == current:
                LOGGER.info("Unchanged; skipped: %s", remote.relative_path)
                totals["skipped"] += 1
                continue

            try:
                response = self.onedrive.open_content_stream(remote.item_id)
                try:
                    metadata = {
                        "source-system": "onedrive",
                        "source-item-id": remote.item_id,
                        "source-etag": remote.etag[:200],
                        "source-modified": remote.modified_at[:200],
                        "source-path": remote.relative_path[:1000],
                    }
                    object_name = self.storage.upload_stream(
                        remote.relative_path,
                        response.raw,
                        remote.mime_type,
                        metadata,
                    )
                    LOGGER.info("Uploaded: %s", object_name)
                finally:
                    response.close()

                known[remote.item_id] = current
                totals["uploaded"] += 1
                state["updated_at"] = datetime.now(timezone.utc).isoformat()
                self.storage.save_state(state)

            except Exception:
                LOGGER.exception("Failed: %s", remote.relative_path)
                totals["failed"] += 1

        if self.mode == "sync":
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.storage.save_state(state)

        return totals
