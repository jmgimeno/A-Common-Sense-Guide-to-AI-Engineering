from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

def llm_response(prompt):
    response = llm.responses.create(
        model="gpt-4.1-nano",
        temperature=0,
        input=prompt
    )
    return response

print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": "You are a helpful AI assistant."},
    {"role": "assistant", "content": "How can I help you today?"}
]

while user_input != "exit":
    history += [{"role": "user", "content": user_input}]

    response = llm_response(history)

    print(f"\nAssistant: {response.output_text}\n")

    history += [
        {"role": "assistant", "content": response.output_text},
    ]

    user_input = input("User: ")