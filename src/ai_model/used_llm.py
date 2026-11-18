from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.23,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)

rate_limiter_longer = InMemoryRateLimiter(
    requests_per_second=0.08,
    check_every_n_seconds=0.1,
    max_bucket_size=1,
)

TEMPERATURE = 0.1
MAX_RETRY = 2

gemini_3_8_flash = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=TEMPERATURE,
    max_tokens=None,
    timeout=None,
    rate_limiter=rate_limiter_longer,
    max_retries=MAX_RETRY,
)

gemini_3_6_flash = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    max_tokens=None,
    timeout=None,
    rate_limiter=rate_limiter_longer,
    max_retries=MAX_RETRY,
)

gemini_3_5_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    rate_limiter=rate_limiter,
    max_retries=MAX_RETRY,
)

LLM = gemini_3_5_flash_lite.with_fallbacks([gemini_3_6_flash, gemini_3_8_flash])
