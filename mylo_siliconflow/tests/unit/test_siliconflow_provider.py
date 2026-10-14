"""Exercise the real SDK request, tool call parsing and tool result replay."""

import json

import httpx
import pytest
from openai import AsyncOpenAI

from mylo.config import load_config
from mylo.llm.provider import ProviderMessage
from mylo.llm.siliconflow_provider import SiliconFlowProvider
from mylo.server.app import _create_provider


async def test_tool_call_round_trip() -> None:
    requests = []

    def respond(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.siliconflow.cn/v1/chat/completions"
        body = json.loads(request.content)
        requests.append(body)
        assert body["max_tokens"] == 1024
        assert "max_completion_tokens" not in body
        assert body["enable_thinking"] is False
        if len(requests) == 1:
            assert body["tools"][0]["function"]["name"] == "query_entities"
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "query_entities",
                            "arguments": '{"domain":"light"}',
                        },
                    }
                ],
            }
            reason = "tool_calls"
        else:
            assert body["model"] == "memory-model"
            assert body["messages"][-1] == {
                "role": "tool",
                "tool_call_id": "call_1",
                "content": '{"light.kitchen":"on"}',
            }
            message = {"role": "assistant", "content": "The kitchen light is on."}
            reason = "stop"
        return httpx.Response(
            200,
            json={
                "id": "test",
                "object": "chat.completion",
                "created": 1,
                "model": body["model"],
                "choices": [{"index": 0, "message": message, "finish_reason": reason}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            },
        )

    provider = SiliconFlowProvider(api_key="test-only")
    await provider._client.close()
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        provider._client = AsyncOpenAI(
            api_key="test-only", base_url=provider._base_url, http_client=client
        )
        messages: list[ProviderMessage] = [{"role": "user", "content": "Which lights are on?"}]
        first = await provider.message(
            system="sys",
            messages=messages,
            tools=[
                {
                    "name": "query_entities",
                    "input_schema": {"type": "object"},
                }
            ],
            model="chat-model",
            max_tokens=1024,
        )
        assert first.stop_reason == "tool_use"
        assert first.tool_calls[0].input == {"domain": "light"}
        assert first.usage == {"input_tokens": 10, "output_tokens": 20}
        messages.extend(
            [
                {"role": "assistant", "content": first.content_blocks},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "call_1",
                            "content": '{"light.kitchen":"on"}',
                        }
                    ],
                },
            ]
        )
        second = await provider.message(
            system="sys", messages=messages, tools=[], model="memory-model", max_tokens=1024
        )
        assert second.stop_reason == "end_turn"
        assert second.text == "The kitchen light is on."


def test_options_and_factory(monkeypatch, tmp_path) -> None:
    options = tmp_path / "options.json"
    options.write_text(
        json.dumps(
            {
                "llm_provider": "siliconflow",
                "api_key": "test-only",
                "model": "custom/model",
                "siliconflow_url": "https://example.com/v1",
            }
        )
    )
    monkeypatch.setenv("MYLO_OPTIONS_FILE", str(options))
    monkeypatch.setenv("MYLO_CONFIG_DIR", str(tmp_path))
    config = load_config()
    assert config.mylo_data_dir == tmp_path / ".mylo-siliconflow"
    assert config.model == "custom/model"
    provider = _create_provider(config)
    assert isinstance(provider, SiliconFlowProvider)
    assert provider._base_url == "https://example.com/v1"
    assert provider._default_model is None  # reconciliation uses its own configured model


@pytest.mark.parametrize(
    "url",
    ["file:///tmp/test", "https://user:pass@example.com/v1", "https://example.com?key=secret"],
)
def test_invalid_endpoint(url) -> None:
    with pytest.raises(ValueError):
        SiliconFlowProvider(api_key="test-only", base_url=url)
