import json
from pathlib import PurePosixPath
import oci


class OCIStorage:
    def __init__(
        self,
        auth_mode,
        config_file,
        config_profile,
        namespace,
        bucket_name,
        prefix,
    ):
        if auth_mode == "resource_principal":
            signer = oci.auth.signers.get_resource_principals_signer()
            self.client = oci.object_storage.ObjectStorageClient(
                config={}, signer=signer
            )
        else:
            config = oci.config.from_file(
                file_location=config_file,
                profile_name=config_profile,
            )
            self.client = oci.object_storage.ObjectStorageClient(config)

        self.upload_manager = oci.object_storage.UploadManager(
            self.client,
            allow_multipart_uploads=True,
            allow_parallel_uploads=False,
        )
        self.namespace = namespace
        self.bucket = bucket_name
        self.prefix = prefix.strip("/")

    def object_name(self, relative_path: str) -> str:
        clean = str(PurePosixPath(relative_path))
        return f"{self.prefix}/{clean}" if self.prefix else clean

    @property
    def state_object_name(self) -> str:
        return "system/sharepoint-sync/state.json"

    def load_state(self) -> dict:
        try:
            response = self.client.get_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=self.state_object_name,
            )
            return json.loads(response.data.content.decode("utf-8"))
        except oci.exceptions.ServiceError as exc:
            if exc.status == 404:
                return {"version": 1, "files": {}}
            raise

    def save_state(self, state: dict) -> None:
        body = json.dumps(state, indent=2, sort_keys=True).encode("utf-8")
        self.client.put_object(
            namespace_name=self.namespace,
            bucket_name=self.bucket,
            object_name=self.state_object_name,
            put_object_body=body,
            content_type="application/json",
        )

    def upload_stream(self, relative_path, stream, content_type, metadata) -> str:
        object_name = self.object_name(relative_path)
        self.upload_manager.upload_stream(
            namespace_name=self.namespace,
            bucket_name=self.bucket,
            object_name=object_name,
            stream_ref=stream,
            part_size=10 * 1024 * 1024,
            content_type=content_type,
            metadata=metadata,
        )
        return object_name
