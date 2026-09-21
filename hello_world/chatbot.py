from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

llm = OpenAI()

response = llm.responses.create(
    model="gpt-4.1",
    temperature=0,
    input="Who was the first person to land on the Moon?"
)

print(response.output_text)
