from threading import active_count
from dotenv import load_dotenv
from openai import OpenAI
import account_manager
import troubleshooter

load_dotenv()
llm = OpenAI()

def llm_response(prompt):
    response = llm.responses.create(
        model="gpt-5-mini",
        input=prompt
    )
    return response

if __name__ == "__main__":
    print(f"Assistant: How can I help you today?\n")
    user_input = input("User: ")
    history = [
        {"role": "developer", "content": f"""You are a customer support technician
        for GROSS, a software product company. You interact with human customers.
        Your specific job is to do intake and route the user to a specialist who can help
        the customer further.

        There are two specialists you can route the customer to:
        1. An account manager. This specialist manages the user account, and can:
           * Retrieve and modify aspects of the customer's profile.
           * Look up the customer's past orders.
           * Help with refunds.
        2. A troubleshooting agent. This specialist helps advise customers on 
        using the GROSS software, of which there are five products:
            * Flamehamster, a web browser.
            * Rumblechirp, an email client.
            * GuineaPigment, a drawing tool for creating/editing SVGs
            * EMRgency, an electronic medical record system
            * Verbiage++, a content management system.

        Do not route the user until you are confident you understand what the user
        is requesting. If you're not sure, keep asking clarifying questions until
        you are sure.

        However, DO NOT try to help the user yourself. Your only job is to route
        them to the right specialist!
        
        As soon as you are confident where the customer needs to be routed to, 
        you can route them by outputting using special notation, as follows:

        To route the user to the account manager, output: [[account]]

        To route the user to the troubleshooting agent, output: [[troubleshoot]] 

        To successfully route the user, you must output the above notation EXACTLY.
        """},
        {"role": "assistant", "content": "How can I help you today?"}
    ]

    while user_input != "exit":
        history += [{"role": "user", "content": user_input}]
        response = llm_response(history)

        if response.output_text in ("[[account]]", "[[troubleshoot]]"):
            break

        print(f"\nAssistant: {response.output_text}\n")

        history += [
            {"role": "assistant", "content": response.output_text},
        ]

        user_input = input("User: ")

    # Route to the appropriate chatbot, passing along the conversation
    # history (minus the intake bot's system prompt):
    if response.output_text == "[[account]]":
        account_manager.run_account_manager(history[1:])
    elif response.output_text == "[[troubleshoot]]":
        troubleshooter.run_troubleshooter(history[1:])