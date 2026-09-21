from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

user_input = input("Assistant: How can I help you today?\n\nUser: ")

while user_input != "exit":
    response = llm.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        input=user_input
    )

    print(f"\nAssistant: {response.output_text}")

    user_input = input("\nUser: ")