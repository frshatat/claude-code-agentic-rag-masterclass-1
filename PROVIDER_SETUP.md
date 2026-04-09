## LLM Provider Setup Guide

The application supports multiple OpenAI-compatible LLM providers. Choose one below and configure via environment variables.

### Quick Start Options

#### 1. **OpenRouter** (Recommended for quick testing)

- **Signup:** https://openrouter.ai (free tier available)
- **No local setup needed** - cloud-based
- **Popular models:** Claude 3.5 Sonnet, GPT-4, Llama 2, and many more

**Setup:**
```bash
# Get your API key from https://openrouter.ai/keys
LLM_PROVIDER=openrouter
LLM_API_ENDPOINT=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-v1-xxxx...  # Your OpenRouter API key
LLM_MODEL_NAME=anthropic/claude-3.5-sonnet  # Or any model from OpenRouter
```

**Cost:** Pay-per-token model. Check pricing at https://openrouter.ai/pricing

---

#### 2. **Ollama** (Local, privacy-focused)

- **Installation:** https://ollama.ai
- **Models available locally:** llama2, neural-chat, mistral, etc.
- **No API key needed** - runs on your machine

**Setup:**
```bash
# 1. Install Ollama and pull a model:
ollama pull llama2

# 2. Start Ollama server (default runs on localhost:11434):
ollama serve

# 3. Configure environment:
LLM_PROVIDER=ollama
LLM_API_ENDPOINT=http://localhost:11434/v1
LLM_API_KEY=ollama  # Placeholder; Ollama doesn't require a real key
LLM_MODEL_NAME=llama2
```

**Note:** Ollama inference is slower than cloud providers due to local processing. First run of a model may take time to load.

---

#### 3. **LM Studio** (Local GPU acceleration)

- **Installation:** https://lmstudio.ai
- **GPU support:** NVIDIA, AMD, Metal (Mac)
- **Interface:** Web-based UI

**Setup:**
```bash
# 1. Download and install LM Studio
# 2. Load a model in LM Studio (e.g., Mistral, Llama 2)
# 3. Enable "Local Server" in LM Studio (Settings → Server)
# 4. Copy the server URL (usually http://localhost:8000)

LLM_PROVIDER=openai-compat  # Generic OpenAI-compatible endpoint
LLM_API_ENDPOINT=http://localhost:8000/v1
LLM_API_KEY=lm-studio  # Placeholder
LLM_MODEL_NAME=<model-name-from-lm-studio>
```

---

#### 4. **Azure OpenAI** (Enterprise, if available)

- **Requires:** Azure subscription + Azure OpenAI resource
- **Endpoint type:** Chat Completions API (not Responses API)
- **Setup cost:** May incur charges based on usage

**Setup:**
```bash
LLM_PROVIDER=openai-compat  # Azure OpenAI endpoints are OpenAI-compatible
LLM_API_ENDPOINT=https://<resource-name>.openai.azure.com/v1
LLM_API_KEY=<your-azure-api-key>
LLM_MODEL_NAME=<deployment-name>  # e.g., gpt-4-deployment
```

**Note:** Ensure your endpoint supports Chat Completions API (not Responses API, which Azure deprecated).

---

### Configuration Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `LLM_PROVIDER` | No | `openrouter` | Default: `openrouter` |
| `LLM_API_ENDPOINT` | Yes | `https://openrouter.ai/api/v1` | Must be OpenAI-compatible HTTP API |
| `LLM_API_KEY` | Yes (mostly) | `sk-or-v1-...` | Can be placeholder for local providers |
| `LLM_MODEL_NAME` | Yes | `anthropic/claude-3.5-sonnet` | Varies by provider |

### Troubleshooting

**"Invalid API key" error:**
- Double-check your API key is correct and not expired
- If using OpenRouter: verify key starts with `sk-or-v1-`

**"Model not found" error:**
- Ensure `LLM_MODEL_NAME` matches a model available on your provider
- OpenRouter: Check https://openrouter.ai for available models
- Ollama: Run `ollama list` to see installed models
- LM Studio: Check model name in LM Studio UI

**"Connection refused" error (local providers):**
- Verify Ollama/LM Studio is running and listening on the configured port
- Check `LLM_API_ENDPOINT` is correct
- Ollama default: `http://localhost:11434`
- LM Studio default: `http://localhost:8000`

**Slow responses:**
- Local providers (Ollama, LM Studio) are slower than cloud (OpenRouter, Azure)
- First inference on a model may take longer (loading from disk)
- Consider using a smaller model for testing (e.g., `mistral` instead of `llama2`)

### Cost Estimation

| Provider | Model Example | Est. Cost/Request | Notes |
|----------|---|---|---|
| OpenRouter | Claude 3.5 Sonnet | $0.002 input / $0.006 output | Pay-per-token |
| Ollama | Llama 2 | $0 | Local, free |
| LM Studio | Mistal | $0 | Local, free |
| Azure OpenAI | GPT-4 | Variable | Subscription model |

---

### For Production

- **Security:** Never commit API keys to version control. Use `.env` (local) or secret management tools (cloud)
- **Rate limiting:** Monitor usage to avoid rate limits on cloud providers
- **Failover:** Consider multi-provider strategy (fallback provider if primary fails)
- **Monitoring:** Use LangSmith integration (already enabled) to track API calls and performance

See `.env.example` for all configurable environment variables.
