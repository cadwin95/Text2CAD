import litellm
import os

response = litellm.completion(
    model="openai/llama.cpp",               # litellm_config.yaml에 정의된 모델명
    api_key="empty",                  # api key to your openai compatible endpoint
    api_base="http://0.0.0.0:4000",     # LiteLLM Proxy를 통해 통신
    messages=[
                {
                    "role": "user",
                    "content": "Hey, how's it going?",
                }
    ],
)
print(response)