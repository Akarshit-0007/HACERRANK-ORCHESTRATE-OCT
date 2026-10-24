import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini_with_backoff(prompt:str,model: str = 'gemini-2.5-flash', max_retries: int = 3, initial_delay: int = 4):
    """
    Safely calls Gemini API with Built in rate limit handling (HTTP -429)
    and exponentially backoff for free-tier constraints.
    :param prompt:
    :param model:
    :param max_retries:
    :param initial_delay:
    :return:
    """

    delay = initial_delay

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model = model,
                contents=prompt,
            )

            usage = getattr(response, 'usage_metadata', None)
            input_tokens = getattr(usage, 'prompt_token_count', 0) if usage else 0
            output_tokens = getattr(usage, 'candidatea_token_count', 0) if usage else 0
            total_tokens = getattr(usage, 'total_token_count', 0) if usage else 0

            result_data = {
                "text": response.text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
            return result_data

        except errors.APIError as e:
            if e.code == 429:
                if attempt == max_retries - 1:
                    print(f"[ERROR] Max retries reached for rate limit. Raising error.")
                    raise e
                print(f"[WARNING] Rate limit hit (429). Waiting {delay}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"[ERROR] Gemini API Error: {e}")
                raise e
        except Exception as e:
            print(f"[ERROR] Unexpected error during model generation: {e}")
            raise e

        return None