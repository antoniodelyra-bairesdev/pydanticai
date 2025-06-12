from os import getenv
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from typing import Any

env = getenv("ENV") or "dev"

credential = (
    ClientSecretCredential(
        tenant_id=getenv("MICROSOFT_GRAPH_TENANT_ID") or "",
        client_id=getenv("MICROSOFT_GRAPH_CLIENT_ID") or "",
        client_secret=getenv("MICROSOFT_GRAPH_CLIENT_SECRET") or "",
    )
    if env != "test"
    else None
)
graph_scopes = ["https://graph.microsoft.com/.default"]

mock: Any = None

client = GraphServiceClient(credential, graph_scopes) if env != "test" else mock
sender_mail = getenv("MICROSOFT_GRAPH_SENDER_MAIL") or ""
