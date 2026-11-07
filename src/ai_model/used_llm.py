from langchain_google_genai import ChatGoogleGenerativeAI

gemini_3_8_flash = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

LLM = gemini_3_8_flash
