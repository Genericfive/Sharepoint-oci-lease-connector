from __future__ import annotations

import json
from pathlib import Path

import msal


class MicrosoftAuthenticator:

    def __init__(self, tenant_id: str, client_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id

        self.cache_dir = Path(".auth")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.cache_dir / "msal_token_cache.json"

        self.cache = msal.SerializableTokenCache()

        if self.cache_path.exists():
            try:
                self.cache.deserialize(
                    self.cache_path.read_text(encoding="utf-8")
                )
            except Exception:
                pass

        authority = (
            f"https://login.microsoftonline.com/{self.tenant_id}"
        )

        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=authority,
            token_cache=self.cache,
        )

        self.scopes = [
            "User.Read",
            "Files.Read.All",
        ]

    def _save_cache(self):
        if self.cache.has_state_changed:
            self.cache_path.write_text(
                self.cache.serialize(),
                encoding="utf-8",
            )

    def get_access_token(self) -> str:
        accounts = self.app.get_accounts()

        result = None

        if accounts:
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0],
            )

        if not result:
            flow = self.app.initiate_device_flow(
                scopes=self.scopes
            )

            if "user_code" not in flow:
                raise RuntimeError(
                    "Could not start Microsoft authentication: "
                    + json.dumps(flow, indent=2)
                )

            print("\nMicrosoft sign-in required")
            print(flow["message"])

            result = self.app.acquire_token_by_device_flow(flow)

        self._save_cache()

        token = result.get("access_token")

        if not token:
            raise RuntimeError(
                result.get(
                    "error_description",
                    "Microsoft authentication failed.",
                )
            )

        return token