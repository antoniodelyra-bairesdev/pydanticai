from httpx import Response as HTTPXResponse


def get_details(response: HTTPXResponse) -> list[str]:
    details = response.json()["detail"]
    details = (
        [details]
        if type(details) == str
        else map(
            lambda detail: detail["msg"],
            details,
        )
    )
    return [*details]
