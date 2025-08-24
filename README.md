# Joblytic — An AI Job Recommender

Joblytic analyzes an uploaded resume and recommends job titles, keywords, and relevant openings by using a Generative AI model (Gemini) and job scrapers (Apify).

Key points
- Fast resume summarization, skills-gap analysis, and a tailored roadmap.
- Job recommendations fetched from LinkedIn and Naukri via Apify actors.
- Uses Google Generative AI (Gemini) as the LLM backend.

Contents
- `app.py` — Streamlit web UI.
- `src/helper.py` — PDF extraction and LLM wrapper (Gemini integration).
- `src/job_api.py` — Job fetching helpers (Apify).
- `requirements.txt` — Python dependencies.

Quick start (Windows / PowerShell)
1. Create & activate a virtual environment (from project root):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Add required environment variables in a `.env` file (do NOT commit `.env`):

```
GEMINI_API_KEY=your_gemini_api_key_here
APIFY_API_KEY=your_apify_api_key_here   # or APIFY_API_TOKEN depending on your setup
```

Notes:
- Do not wrap keys in quotes. Example: `GEMINI_API_KEY=AIza...` (no surrounding quotes).
- If `job_api.py` expects `APIFY_API_TOKEN`, either rename your `.env` key or update `job_api.py` to read `APIFY_API_KEY`.

4. Run the app:

```powershell
streamlit run app.py
```

What to add to git / what to ignore
- Keep in repo: source code (`app.py`, `src/`), `requirements.txt`, `README.md`, `pyproject.toml` (if present).
- Ignore: `.env`, `.venv/`, editor settings (`.vscode/`, `.idea/`), and other secrets or build artifacts.

Suggested `.gitignore` entries
```
.venv/
.env
# Python
__pycache__/
*.py[cod]

# Editors
.vscode/
.idea/
```

Troubleshooting (common issues)
- ModuleNotFoundError on import (e.g., `google.generativeai`): ensure the virtualenv is activated and `pip install -r requirements.txt` was run in the same environment.
- `API key not valid` / `DefaultCredentialsError`: verify `GEMINI_API_KEY` in `.env` and mirror it into `GOOGLE_API_KEY` if required. Restart the shell after editing `.env`.
- Quota / Rate limit errors (429 / ResourceExhausted): reduce request frequency/tokens, enable billing or request quota increases in Google Cloud, or add retry/backoff (helper includes basic retries).

Security
- You exposed an API key in the repository workspace; rotate that key in Google Cloud immediately and update `.env` with the new key.
- Add `.env` to `.gitignore` and never commit secrets.

Next steps / improvements
- Add caching for repeated prompts (to reduce LLM calls).
- Add unit tests for `src/helper.py` and `src/job_api.py`.
- Provide a Dockerfile for easier deployment.

