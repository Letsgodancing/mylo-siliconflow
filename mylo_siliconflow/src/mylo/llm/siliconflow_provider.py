"""SiliconFlow chat completions with the shared Mylo tool-call conversion."""

from urllib.parse import urlsplit

from mylo.llm.openai_provider import OpenAIProvider

DEFAULT_SILICONFLOW_URL = "https://api.siliconflow.cn/v1"


class SiliconFlowProvider(OpenAIProvider):
    def __init__(self, api_key: str, *, base_url: str = DEFAULT_SILICONFLOW_URL) -> None:
        url = urlsplit(base_url)
        if url.scheme not in ("https", "http") or not url.hostname or url.username or url.password:
            raise ValueError("siliconflow_url must be an HTTP(S) URL without credentials")
        if url.query or url.fragment:
            raise ValueError("siliconflow_url must not contain a query or fragment")
        super().__init__(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            legacy_max_tokens=True,
            disable_thinking=True,
        )
