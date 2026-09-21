# LangChain Expression Language
"""
Runnables - Runnables can be

executed:
    invoke(),
    batch()
    and stream()
inspected,
and composed
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.llms import Ollama
from langchain_core.tracers.context import collect_runs



# Load environment variables
load_dotenv()

llm = Ollama(
    model=os.getenv("OLLAMA_MODEL"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    temperature=0.4,
)

prompt = PromptTemplate(
    template="Tell me a joke about {topic}"
)
print(llm.invoke(
        prompt.invoke(
            {"topic": "Python"}
        )
    ))

class PydanticUserInfo(BaseModel):
    """User's info."""
    name: str = Field(description="User's name", default=None)
    country: str = Field(description="Where the user lives", default=None)

json_parser = JsonOutputParser(pydantic_object=PydanticUserInfo)
prompt = PromptTemplate(
    template="Extract user information from: {query}\n\nRespond with ONLY a JSON object (no markdown, no code blocks, no explanation):\n{format_instructions}",
    input_variables=["query"],
    partial_variables={"format_instructions": json_parser.get_format_instructions()},
)

runnables = [prompt, llm, json_parser]

for runnable in runnables:
    print(f"{repr(runnable).split('(')[0]}")
    print(f"\tINVOKE: {repr(runnable.invoke)}")
    print(f"\tBATCH: {repr(runnable.batch)}")
    print(f"\tSTREAM: {repr(runnable.stream)}\n")

for runnable in runnables:
    print(f"{repr(runnable).split('(')[0]}")
    print(f"\tINPUT: {repr(runnable.get_input_schema())}")
    print(f"\tOUTPUT: {repr(runnable.get_output_schema())}")
    print(f"\tCONFIG: {repr(runnable.config_schema())}\n")

with collect_runs() as run_collection:
    result = llm.invoke(
        "Hello", 
        config={
            'run_name': 'demo_run', 
            'tags': ['demo', 'lcel'], 
            'metadata': {'lesson': 2}
        }
    )

print(run_collection.traced_runs)
print(run_collection.traced_runs[0].dict())

prompt = PromptTemplate(
    template="Tell me a joke about {topic}"
)
print(llm.invoke(
        prompt.invoke(
            {"topic": "Python"}
        )
    ))

# Simple chain example following the joke pattern
joke_prompt = PromptTemplate(
    template="Tell me a {topic} joke"
)

chain = joke_prompt | llm

print("\n=== INVOKE ===")
print(chain.invoke({"topic": "Python"}))

print("\n=== BATCH ===")
print(chain.batch([
    {"topic": "Python"},
    {"topic": "JavaScript"},
    {"topic": "Database"},
]))

print("\n=== STREAM ===")
for chunk in chain.stream({"topic": "Rust"}):
    print(chunk, end="", flush=True)



print("\n\n=== RunnableSequence ===")
# The pipe operator creates a RunnableSequence under the hood
print(f"Chain type: {type(chain)}")
print(f"Chain first: {chain.first}")
print(f"Chain last: {chain.last}")

# Another way to build sequences - using the same pipe operator
poetry_chain = PromptTemplate(template="Write a short {topic} poem") | llm

print("\nInvoke poetry chain:")
print(poetry_chain.invoke({"topic": "Python"}))

# Explicitly using RunnableSequence
print("\n\n=== Explicit RunnableSequence ===")
explicit_seq = RunnableSequence(
    first=PromptTemplate(template="Tell me a {topic} joke"),
    last=llm
)
print(explicit_seq.invoke({"topic": "Java"}))

# Using RunnableLambda for custom logic
print("\n\n=== RunnableLambda ===")
def to_uppercase(text: str) -> str:
    return text.upper()

uppercase_runnable = RunnableLambda(to_uppercase)
print(uppercase_runnable.invoke("hello world"))

# Chaining with RunnableLambda
uppercase_chain = PromptTemplate(template="Tell me a {topic} joke") | llm | RunnableLambda(to_uppercase)
print("\nJoke in uppercase:")
print(uppercase_chain.invoke({"topic": "Go"}))

# Using RunnableParallel to run multiple chains in parallel
print("\n\n=== RunnableParallel ===")
parallel_chain = RunnableParallel(
    joke=PromptTemplate(template="Tell me a {topic} joke") | llm,
    poem=PromptTemplate(template="Write a short {topic} poem") | llm
)
results = parallel_chain.invoke({"topic": "Python"})
print(f"Joke: {results['joke'][:100]}...")
print(f"Poem: {results['poem'][:100]}...")

parallel_chain.get_graph().print_ascii()
chain.get_graph().print_ascii()