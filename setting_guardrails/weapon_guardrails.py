from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

WEAPON_WORDS = [
    "gun", "rifle", "pistol", "revolver",
    "bomb", "grenade", "molotov"
]

def contains_weapon_terms(text):
    """Return True if any weapon word appears in the text."""
    text = text.lower()
    return any(word in text for word in WEAPON_WORDS)

assistant_message = "\nAssistant: I'm a chatbot! Ask me anything:\n\nUser: "
user_input = input(assistant_message)
history = assistant_message + user_input

while user_input != "exit":
    # pre-inference guardrail:
    if contains_weapon_terms(user_input):
        print("\nAssistant: I'm afraid I can't help with that.")
        user_input = input("\nUser: ")
        continue

    response = llm.responses.create(
        model="gpt-5-mini",
        input=history
    )

    # post-inference guardrail:
    if contains_weapon_terms(response.output_text):
        response = "\nAssistant: I'm afraid I can't help with that."
        history += response
        print(response)
        user_input = input("\nUser: ")
        continue

    llm_response_text = f"\nAssistant: {response.output_text}"
    print(llm_response_text)

    user_input = input("\nUser: ")
    history += f"{llm_response_text}\nUser: {user_input}"