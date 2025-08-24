
import fitz #PyMuPDF
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

load_dotenv()

# Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set. Add GEMINI_API_KEY=your_key in .env or set it in the environment before running the app.")

# Some underlying Google clients look for GOOGLE_API_KEY or Application Default Credentials.
# Mirror the GEMINI_API_KEY into GOOGLE_API_KEY so low-level clients accept the key.
os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file.
    
    Args:
        uploaded_file (str): The path to the PDF file.
        
    Returns:
        str: The extracted text.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text



def ask_gemini(prompt, max_tokens=500, retries=4, initial_backoff=1.0):
    """
    Sends a prompt to Gemini with retries/backoff for quota errors and returns the response.

    - Lists available models and tries suitable ones.
    - Retries on ResourceExhausted (quota) errors with exponential backoff.
    """
    # Build a list of available models from the SDK so we try only valid names
    try:
        models_iter = genai.list_models()
        available = [getattr(m, "name", None) or getattr(m, "id", None) or str(m) for m in models_iter]
    except Exception as e:
        raise RuntimeError(f"Could not list Gemini models: {e}") from e

    # Prefer models that look like chat/text/gemini/bison
    prefer = [m for m in available if any(k in m.lower() for k in ("gemini", "bison", "chat", "text"))]
    candidate_models = prefer or available

    last_exc = None
    for model_name in candidate_models:
        backoff = initial_backoff
        for attempt in range(retries):
            try:
                # Try top-level helper if available
                if hasattr(genai, "generate_text"):
                    resp = genai.generate_text(model=model_name, prompt=prompt, max_output_tokens=max_tokens)
                    if hasattr(resp, "text"):
                        return resp.text
                    return str(resp)

                # Fallback to GenerativeModel interface
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt, generation_config={"max_output_tokens": max_tokens})
                if hasattr(response, "text"):
                    return response.text
                return str(response)

            except google_exceptions.ResourceExhausted as e:
                # quota exhausted - respect server delay if provided, otherwise exponential backoff
                last_exc = e
                retry_delay = getattr(e, 'retry_delay', None)
                sleep_secs = backoff
                if retry_delay and hasattr(retry_delay, 'seconds'):
                    sleep_secs = max(sleep_secs, retry_delay.seconds)
                time.sleep(sleep_secs)
                backoff *= 2
                continue
            except Exception as e:
                # model not found / not supported -> try next model, other errors propagate
                last_exc = e
                msg = str(e).lower()
                if 'not found' in msg or 'not supported' in msg or 'model' in msg and 'not found' in msg:
                    break
                raise

    raise RuntimeError(f"No usable model found for Gemini. Tried: {candidate_models}. Last error: {last_exc}")


# Backwards compatibility: provide ask_openai with same signature that forwards to Gemini
def ask_openai(prompt, max_tokens=500):
    """Compatibility wrapper for code that calls ask_openai; forwards to Gemini implementation."""
    return ask_gemini(prompt, max_tokens=max_tokens)
