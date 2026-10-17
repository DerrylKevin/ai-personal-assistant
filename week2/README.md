# Week 2: Model quickstarts

Run every command from the repo root (`ai-personal-assistant/`), not from inside `week2/`.

## 1. Add dependencies

```
uv add openai typesafe-sdk==0.7.0 ollama ipykernel
```

| Package | Used by |
| --- | --- |
| `openai` | `openai-quickstart.py`, `structured_output.py` |
| `typesafe-sdk` | `jev-quickstart.py` |
| `ollama` | `ollama-quickstart.py` |
| `ipykernel` | `pydantic-introduction.ipynb` |

## 2. Set up keys and downloads

**You only need to set up one of the three options below, not all of them.**

- **OpenAI is the easiest to set up for general tasks.** It needs a paid API key.
- **Ollama is free.** It runs on your laptop and needs no key.
- **TypeSafe (Jev) is optional.** Set it up only if you want to try the decision model.

Week 3's spam workflow uses OpenAI, so OpenAI is the best choice if you plan to continue.

Put any keys in your `.env` file, never in `.env.example` or in code.

- **OpenAI key:** Create one at https://platform.openai.com/api-keys and add it as `OPENAI_API_KEY=...`.
- **TypeSafe (Jev) key:** Log in at https://console.typesafe.ai/playground, create a key at https://console.typesafe.ai/keys, and add it as `TYPESAFE_API_KEY=...`.
- **Ollama (no key):** Download it from https://ollama.com/download, then run `ollama pull qwen2.5:3b-instruct`.

## 3. Run the files for your option

Run only the files for the option you set up. `structured_output.py` also uses OpenAI. The Pydantic notebook needs no key.

| File | Command |
| --- | --- |
| `openai-quickstart.py` | `uv run week2/openai-quickstart.py` |
| `structured_output.py` | `uv run week2/structured_output.py` |
| `jev-quickstart.py` | `uv run week2/jev-quickstart.py` |
| `ollama-quickstart.py` | `uv run week2/ollama-quickstart.py` |
| `pydantic-introduction.ipynb` | Open it in VS Code or Cursor and select the `.venv` Python kernel |
