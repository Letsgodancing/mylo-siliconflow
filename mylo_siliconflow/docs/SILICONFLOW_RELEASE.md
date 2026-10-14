Mylo SiliconFlow 1.9.0.1 is based on upstream Mylo v1.9.0.

- Adds SiliconFlow OpenAI-compatible chat completions and function calling, with API key, model and endpoint in Home Assistant add-on options.
- Uses max_tokens and disables thinking for tool-call compatibility. Choose a model supporting function calling and non-thinking mode.
- Preserves upstream tools, approvals, backup/rollback, memory and Anthropic/OpenAI/Gemini/Ollama providers.
- Uses an independent add-on slug and .mylo-siliconflow data directory.
- Builds amd64 and aarch64 images exclusively under ghcr.io/letsgodancing.

Validation: the release workflow runs unit tests and checks anonymous image manifest/layer access before publishing this release. No live SiliconFlow API key or HAOS instance is used in automated tests. Actual Home Assistant operations and paid model calls require integration testing. Cost estimates for unpriced models use upstream fallback rates and are not SiliconFlow billing figures.
