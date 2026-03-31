import httpx
import os


class GroqProvider:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    }
                )
                print("GROQ KEY:", self.api_key)
                if response.status_code != 200:
                    print("❌ GROQ ERROR:", response.text)
                    return ""

                data = response.json()
                print("GROQ KEY:", self.api_key)

                return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print("❌ GROQ EXCEPTION:", str(e))
            return ""