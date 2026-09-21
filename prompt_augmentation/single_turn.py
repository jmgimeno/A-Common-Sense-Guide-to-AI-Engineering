from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

user_input = input("I'm a helpful chatbot! Ask me anything:\n")

response = llm.responses.create(
    model="gpt-4.1-mini",
    temperature=0,
    input=user_input
)

print(response.output_text)
