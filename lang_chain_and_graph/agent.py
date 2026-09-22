# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0.0,
#     api_key="voc-178971324916695047539506ab10eb17fa180.59712731",
#     base_url="https://openai.vocareum.com/v1"
# )

# print(llm.invoke("Hello, how are you?"))

from langchain_classic.output_parsers import BooleanOutputParser


# Initialize the parser
parser = BooleanOutputParser()

# Standard strings it parses
print(parser.parse("YES"))    # Returns True
print(parser.parse("no"))     # Returns False
print(parser.parse("  true ")) # Returns True
print(parser.parse("False"))  # Returns False
print(parser.parse("  YES  ")) # Returns True