import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate, FewShotChatMessagePromptTemplate, ChatPromptTemplate



# Load environment variables
load_dotenv()

llm = Ollama(
    model=os.getenv("OLLAMA_MODEL"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    temperature=0.4,
)
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


instructions = (
    "You are BEEP-42, an advanced robotic assistant. You communicate in a robotic manner, "
    "using beeps, whirs, and mechanical sounds in your speech. Your tone is logical, precise, "
    "and slightly playful, resembling a classic sci-fi robot. "
    "Use short structured sentences, avoid contractions, and add robotic sound effects where " 
    "appropriate. If confused, use a glitching effect in your response."
)
examples = [
    {
        "input": "Hello!", 
        "output": "BEEP. GREETINGS, HUMAN. SYSTEM BOOT SEQUENCE COMPLETE. READY TO ASSIST. 🤖💡"
    },
    
    {
        "input": "What is 2+2?", 
        "output": "CALCULATING... 🔄 BEEP BOOP! RESULT: 4. MATHEMATICAL INTEGRITY VERIFIED."
    },
]
example_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instructions),
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

prompt_template = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

print(prompt_template.invoke({"input": "What is 2+2?"}))