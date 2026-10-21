from python_shared.http import ResilientHttpClient
from shared.ports.embedding_provider import EmbeddingProviderPort, EmbeddingRequest, EmbeddingResponse
from shared.utils.hash import stable_embedding_key


class CloudflareEmbeddingClient(EmbeddingProviderPort):
    def __init__(self, account_id: str, api_token: str, profile: str = "api_service") -> None:
        self.account_id: str = account_id
        self.api_token: str = api_token
        self._client: ResilientHttpClient = ResilientHttpClient(timeout=10.0, profile=profile)

    def create_embedding(self, request: EmbeddingRequest, *, dimensions: int) -> EmbeddingResponse:
        if not self.account_id or not self.api_token or self.account_id == "local-account":
            return EmbeddingResponse(
                embedding_key=stable_embedding_key(request.trace_id, request.span_id, request.text, prefix="emb_"),
                dimensions=dimensions,
                provider="cloudflare",
            )

        model = request.model or "@cf/baai/bge-small-en-v1.5"
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{model}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        resp = self._client.post(url, headers=headers, json={"text": request.text})
        resp.raise_for_status()

        return EmbeddingResponse(
            embedding_key=stable_embedding_key(request.trace_id, request.span_id, request.text, prefix="emb_"),
            dimensions=dimensions,
            provider="cloudflare",
        )
