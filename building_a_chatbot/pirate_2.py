from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

developer_message = """What follows below is a conversation between a pirate
                    AI assistant and a human user:"""
assistant_message = "Assistant: Arrgh, how can I help you, matey?\n\nUser: "
user_input = input(assistant_message)
history = developer_message + assistant_message + user_input

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