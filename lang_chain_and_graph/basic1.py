import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate



# Load environment variables
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

messages = [
  SystemMessage(content="You are a helpful assistant."),
  HumanMessage(content="What's the capital of Brazil?"),
  AIMessage(content="The capital of Brazil is Brasília."),
  HumanMessage(content="What's the capital of Canada?")
]

# response = llm.invoke(messages)
# print(response)

prompt_template = PromptTemplate(
    template="What is the capital of {country}?",
)

print(prompt_template.invoke({"country": "Canada"}))
print(llm.invoke(prompt_template.invoke({"country": "Canada"})))