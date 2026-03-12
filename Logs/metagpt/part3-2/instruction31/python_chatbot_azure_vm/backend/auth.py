class AuthManager:
    """
    Handles basic token authentication for the backend API.
    """

    def __init__(self, valid_token: str):
        if not valid_token:
            raise ValueError("A valid API authentication token must be provided.")
        self.valid_token = valid_token

    def verify_token(self, token: str) -> bool:
        """
        Verifies that the provided token matches the expected API token.
        """
        return token == self.valid_token