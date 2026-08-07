import msal


class MicrosoftTokenProvider:
    def __init__(self, auth_mode, tenant_id, client_id, client_secret, token_cache_file):
        self.auth_mode = auth_mode
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_cache_file = token_cache_file

    def get_access_token(self) -> str:
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"

        if self.auth_mode == "client_credentials":
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret,
            )
            result = app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            return self._extract(result)

        cache = msal.SerializableTokenCache()
        self.token_cache_file.parent.mkdir(parents=True, exist_ok=True)
        if self.token_cache_file.exists():
            cache.deserialize(self.token_cache_file.read_text(encoding="utf-8"))

        app = msal.PublicClientApplication(
            self.client_id,
            authority=authority,
            token_cache=cache,
        )

        scopes = ["User.Read", "Files.Read.All"]
        result = None
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(scopes=scopes, account=accounts[0])

        if not result:
            flow = app.initiate_device_flow(scopes=scopes)
            if "user_code" not in flow:
                raise RuntimeError(f"Could not start Microsoft device flow: {flow}")
            print(flow["message"])
            result = app.acquire_token_by_device_flow(flow)

        if cache.has_state_changed:
            self.token_cache_file.write_text(cache.serialize(), encoding="utf-8")

        return self._extract(result)

    @staticmethod
    def _extract(result: dict) -> str:
        token = result.get("access_token")
        if not token:
            raise RuntimeError(
                "Microsoft authentication failed: "
                + result.get("error_description", str(result))
            )
        return token
