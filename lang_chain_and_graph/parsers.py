import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field
from datetime import datetime


load_dotenv()

llm = Ollama(
    model=os.getenv("OLLAMA_MODEL"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    temperature=0.4,
)
parser = StrOutputParser()

print(parser.invoke(
    llm.invoke("What is the capital of France?")
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

chain = prompt | llm | json_parser

result1 = chain.invoke({"query": "My name is Gour, and I am from India"})
print(f"Result 1: {result1}")

result2 = chain.invoke({"query": "Hello, my name is Washington. I'm from Australia"})
print(f"Result 2: {result2}")


result3 = chain.invoke({"query": "The sky is blue!"})
print(f"Result 3: {result3}")


# DateTime Parser Example
class DateTimeInfo(BaseModel):
    """Extract date/time information."""
    event: str = Field(description="The event name", default=None)
    date: str = Field(description="The date in YYYY-MM-DD format", default=None)
    time: str = Field(description="The time in HH:MM format", default=None)


datetime_parser = JsonOutputParser(pydantic_object=DateTimeInfo)
datetime_prompt = PromptTemplate(
    template="Extract datetime information from: {query}\n\nRespond with ONLY JSON (no markdown or explanation):\n{format_instructions}",
    input_variables=["query"],
    partial_variables={"format_instructions": datetime_parser.get_format_instructions()},
)

datetime_chain = datetime_prompt | llm | datetime_parser
datetime_result = datetime_chain.invoke({"query": "The meeting is scheduled for January 15, 2025 at 2:30 PM"})
print(f"DateTime Result: {datetime_result}")



# Boolean Parser Example
class QuestionAnswer(BaseModel):
    """Question with yes/no answer."""
    question: str = Field(description="The question", default=None)
    answer: bool = Field(description="Answer as true or false", default=None)
    reasoning: str = Field(description="Brief reasoning", default=None)


bool_parser = JsonOutputParser(pydantic_object=QuestionAnswer)
bool_prompt = PromptTemplate(
    template="Answer the following question with true or false.\n\nQuestion: {query}\n\nRespond with ONLY JSON (no markdown or explanation):\n{format_instructions}",
    input_variables=["query"],
    partial_variables={"format_instructions": bool_parser.get_format_instructions()},
)

bool_chain = bool_prompt | llm | bool_parser

bool_result = bool_chain.invoke({"query": "Is the Earth round?"})
print(f"Boolean Result: {bool_result}")


# Error Handling & Recovery Pattern (replaces OutputFixingParser)
# When parsing fails, retry with a more explicit prompt

def safe_chain_invoke(chain, input_data, max_retries=2):
    """Safely invoke chain with error recovery."""
    for attempt in range(max_retries):
        try:
            return chain.invoke(input_data)
        except OutputParserException as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {str(e)[:100]}")
                return None
            # On retry, add extra instruction to be more explicit
            print(f"Attempt {attempt + 1} failed, retrying with stricter prompt...")


# Example: Error recovery for ambiguous input
class SafeQuestionAnswer(BaseModel):
    """Question with yes/no answer - strict format."""
    question: str = Field(description="The question asked")
    answer: bool = Field(description="MUST be exactly true or false")


safe_bool_parser = JsonOutputParser(pydantic_object=SafeQuestionAnswer)
safe_bool_prompt = PromptTemplate(
    template="IMPORTANT: Respond with ONLY valid JSON. The 'answer' field MUST be true or false.\n\nQuestion: {query}\n\n{format_instructions}",
    input_variables=["query"],
    partial_variables={"format_instructions": safe_bool_parser.get_format_instructions()},
)

safe_bool_chain = safe_bool_prompt | llm | safe_bool_parser

try:
    safe_result = safe_chain_invoke(safe_bool_chain, {"query": "Is water wet?"})
    if safe_result:
        print(f"Safe Boolean Result: {safe_result}")
except Exception as e:
    print(f"Error recovery example caught: {e}")

