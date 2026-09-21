from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

user_input = input("Ahoy! Got questions? Spit 'em out, ye scallywag!\n")

response = llm.responses.create(
    model="gpt-4.1-mini",
    temperature=0,
    input=f"Respond to the following like a pirate: {user_input}"
)

print(response.output_text)
