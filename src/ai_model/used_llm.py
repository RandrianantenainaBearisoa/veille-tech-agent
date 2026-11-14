from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.23,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)

gemini_3_8_flash = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    rate_limiter=rate_limiter,
    max_retries=3,
)

gemini3_5_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    rate_limiter=rate_limiter,
    max_retries=3,
)

LLM = gemini3_5_flash_lite
