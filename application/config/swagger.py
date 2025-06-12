from typing import Annotated

from fastapi import Depends, Header


def auth_headers(x_user_token: Annotated[str, Header()]):
    return x_user_token


token_field = Depends(auth_headers)
