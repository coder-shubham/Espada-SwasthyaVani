import ollama
import sys
from typing import List, Dict, Any

sys.path.append('.')

class OllamaLlama3Client:
    
    def __init__(self, model_name: str = "llama3.1:8b", temperature: float = 0.0, max_tokens: int = 1024):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def create_message(self, role: str, content: str) -> Dict[str, str]:
        if role not in ("system", "user", "assistant"):
            raise ValueError(f"Invalid role: {role}. Role must be 'system', 'user', or 'assistant'.")
        return {"role": role, "content": content}

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={"num_ctx": self.max_tokens, "temperature": self.temperature}
            )
            if 'message' in response and 'content' in response['message']:
                return response['message']['content']
            else:
                print("Error: Unexpected response format from Ollama.")
                return ""

        except ollama.ResponseError as e:
            print(f"Error from Ollama: {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ""

    def stream_response(self, messages: List[Dict[str, str]]) -> Any:
        try:
            stream = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=True,
                options={"num_ctx": self.max_tokens, "temperature": self.temperature}
            )
            return stream
        except ollama.ResponseError as e:
            print(f"Error from Ollama: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


## testing purpose only
if __name__ == "__main__":
    
    from factory.config import FactoryConfig
    print("Make sure you have Ollama installed and the Llama 3.1 8b model is downloaded using Ollama.")
    print("Once Ollama is running, you can download the Llama 3.1 model by running:")
    print("ollama run llama3.1:8b")


    messages = [
        FactoryConfig.llm.create_message(
            role="system",
            content="You are a helpful medical scheme assistant.  You answer concisely. You will be given a query and some context, whatever the language of the query is, respond the answer in that language only. You should not go beyond context, answer strictly from the provided context only.",
        ),
        FactoryConfig.llm.create_message(role="user", content="Query: आयुष्मान भारत योजना के लिए पात्रता कैसे जांचें?. Context: To apply, you need to check your eligibility using your Aadhaar card."),
    ]


    response = FactoryConfig.llm.generate_response(messages)
    
    print(response)
