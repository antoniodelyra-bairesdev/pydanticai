class IntegrationApiException(Exception):
    pass


class IntegrationApiRequestException(IntegrationApiException):
    def __init__(self, api_name: str, message: str | None = None):
        if message is None:
            message = ""

        super().__init__(f"{api_name}: {message}")


class IntegrationApiClientNotOpenException(IntegrationApiException):
    def __init__(self, api_name: str):
        super().__init__(f"{api_name}: client HTTP não definido ou fechado.")
