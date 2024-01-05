class HTTPException(Exception):

    def __init__(self, status_code: int, detail: str = None):
        self.status_code = status_code
        self.detail = detail


class EnpointParseException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
