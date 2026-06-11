import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not found.")
        return
    
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
    try:
        # Try a known good model
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print(f"Success! Model: {completion.model}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_groq()
