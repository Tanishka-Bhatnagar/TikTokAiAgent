import time

class OAuthService:
    def __init__(self):
        self.token = None
        self.expiry = None

    def authorize(self, client_id, client_secret):
        if client_id != "valid_client_id" or client_secret != "valid_client_secret":
            return None, "Invalid client ID or client secret."

        self.token = "mock_access_token"
        self.expiry = time.time() + 60  # token valid for 60 seconds
        return self.token, None

    def is_token_valid(self):
        if not self.token:
            return False, "No access token found."
        if time.time() > self.expiry:
            return False, "Access token expired."
        return True, None
