import httpx


class YFSymbolNotFound(BaseException):
    def __init__(self, symbol: str) -> None:
        super().__init__(
            f"Symbol '{symbol}' not found in yahoo-finance, it may be "
            "delisted or renamed."
        )


class YFUnprocessableEntity(BaseException):
    def __init__(self, symbol: str, response: httpx.Response) -> None:
        error = response.json().get("chart", {}).get("error")
        if isinstance(error, dict):
            message = (
                f"Yahoo-finance chart response error for symbol '{symbol}': "
                f"{error.get('description')}"
            )
        else:
            message = (
                f"Yahoo-finance chart response error for symbol '{symbol}': "
                "Unprocessable Entity"
            )
        super().__init__(message)
