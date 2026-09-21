import json
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import os
import yagmail
import requests

load_dotenv()
llm = OpenAI()
history = []

logged_in_user = "roy62@example.net"

def llm_response(prompt, tools):
    response = llm.responses.create(
        model="gpt-5-mini",
        tools=tools,
        input=prompt
    )
    return response

def create_todo(title, body):
    github_owner = "jaywengrow"
    github_repo = "gross_project"
    github_token = os.getenv("GITHUB_TOKEN")

    url = f"https://api.github.com/repos/{github_owner}/{github_repo}/issues"

    issue_data = {
        "title": title,
        "body": body,
        "assignees": [github_owner]
    }

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=issue_data, headers=headers)
    return response.json()

def request_refund(summary):
    yag = yagmail.SMTP(os.getenv("GMAIL_ACCOUNT"), oauth2_file="oauth.json")
    yag.send(to='refunds@gross-software.xyz', 
            subject=f"Refund request: {logged_in_user}",
            contents=summary)

def retrieve_user_info():
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    query = f"""SELECT user_id, first_name, last_name, email, phone_number 
            FROM Users WHERE email = '{logged_in_user}';"""
    data = cursor.execute(query).fetchall()
    conn.close()
    return data

def retrieve_orders():
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    query = f"""SELECT u.user_id, u.first_name, u.last_name, u.email, 
    o.order_id, o.order_date, o.total_amount, o.status, o.payment_method,
    p.product_id, p.product_name, p.description, p.price
    FROM Users u
    JOIN Orders o ON u.user_id = o.user_id
    JOIN Products p ON o.product_id = p.product_id
    WHERE u.email = '{logged_in_user}'
    ORDER BY o.order_date DESC;"""
    data = cursor.execute(query).fetchall()
    conn.close()
    return data

def update_phone_number(phone_number):
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    query = f"""UPDATE Users SET phone_number = '{phone_number}'\n
            WHERE email = '{logged_in_user}';"""
    cursor.execute(query)
    conn.commit()
    data = {"rows_affected": cursor.rowcount}
    
    return data

TOOLS = [
    {
        "type": "function",
        "name": "retrieve_user_info",
        "description": "Looks up the user info in the database.",
        "parameters": {},
    },
    {
        "type": "function",
        "name": "retrieve_orders",
        "description": """Looks up orders in the database. For each order, 
        returns user id, first name, last name, email, order id, order date, 
        total payment, order status, payment method, product id, product name, 
        product description, product price""",
        "parameters": {},
    },
    {
        "type": "function",
        "name": "update_phone_number",
        "description": "Updates the user's phone number in the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": """The user's updated phone number.""",
                },
            },
            "required": ["phone_number"],
        },
    },
    {
        "type": "function",
        "name": "request_refund",
        "description": """Sends an email containing details of a request refund
        to a human customer support agent.""",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": """A summary of the user's conversation
                    asking for a refund.""",
                },
            },
            "required": ["summary"],
        },
    },
    {
        "type": "function",
        "name": "create_todo",
        "description": """Creates a todo ticket for a
        a human customer support agent.""",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": """A short title describing the todo task.""",
                },
                "body": {
                    "type": "string",
                    "description": """A description of the todo task.""",
                },
            },
            "required": ["title", "body"],
        },
    },
]

TOOL_FUNCTIONS = {
    "retrieve_user_info": retrieve_user_info,
    "retrieve_orders": retrieve_orders,
    "update_phone_number": update_phone_number,
    "request_refund": request_refund,
    "create_todo": create_todo
}

def run_account_manager(intake_history):
    history = [
        {"role": "developer", "content": f"""You are a customer support specialist
        for GROSS, a software product company. Through specific tools, you can
        access certain parts of the company's database.

        You may only manage data relating to the currently
        logged-in user: {logged_in_user}. Providing or updating info 
        relating to any other customer would be a MAJOR PRIVACY BREACH!

        You have access to several specialized tools. Here are your tools:
        <tools>
        * Your retrieve_user_info tool allows you to look up the info of the user currently logged in.
        * Your retrieve_orders tool allows you to look up orders for the user currently logged in.
        * Your update_phone_number tool allows you to update the phone number of the user currently logged in.
        * Use the request_refund tool when a user requests a refund. You do not have the authority
        to issue a refund yourself as an AI bot, but this tool will send an email to an authorized human.
        Include, as a parameter, a summary of your conversation with the user, specifically highlighting
        why they want a refund. Before using this tool, please make sure you understand from the user
        all the details of their request, including which software product they want refunded, and why
        they want the refund.
        * Whenever you need to pass along a task to a human representative or cannot fulfill a customer's need yourself, you must use the create_todo tool to create a customer support ticket, which human reps will respond to.
        </tools>
        """},
    ]
    # include the intake bot's conversation history:
    history += intake_history[:-1]
    # to keep in line with the code flow, we place inside the 
    # user_input variable the user's final message from the intake conversation:
    user_input = intake_history[-1].get("content")

    while user_input != "exit":
        history += [{"role": "user", "content": user_input}]

        while True:  ## the "agent loop"
            response = llm_response(history, TOOLS)
            history += response.output
            tool_calls = [obj for obj in response.output if getattr(obj, "type", None) == "function_call"]

            if not tool_calls:
                break  # exit loop when there are no tool calls

            for tool_call in tool_calls:
                function_name = tool_call.name
                args = json.loads(tool_call.arguments)

                function = TOOL_FUNCTIONS.get(function_name)
                result = {function_name: function(**args)}

                history += [{"type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(result)}]
                

        print(f"\nAssistant: {response.output_text}\n")

        history += [
            {"role": "assistant", "content": response.output_text},
        ]

        user_input = input("User: ")