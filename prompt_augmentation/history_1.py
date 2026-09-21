from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

assistant_message = "Assistant: How can I help you today?\n\nUser: "
user_input = input(assistant_message)
history = assistant_message + user_input

while user_input != "exit":
    response = llm.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        input=history
    )

    llm_response_text = f"\nAssistant: {response.output_text}"
    print(llm_response_text)

    user_input = input("\nUser: ")
    history += f"{llm_response_text}\nUser: {user_input}"