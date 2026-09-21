import json
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import os
import requests

load_dotenv()
llm = OpenAI()

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
    "create_todo": create_todo
}


print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
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
    * Whenever you need to pass along a task to a human representative or cannot fulfill a customer's need yourself, you must use the create_todo tool to create a customer support ticket, which human reps will respond to.
    </tools>
    """},
    {"role": "assistant", "content": "How can I help you today?"},
    {"role": "user", "content": user_input}
]

while user_input != "exit":
    while True:  ## the "agent loop"
        response = llm_response(history, TOOLS)
        history += response.output
        tool_calls = [obj for obj in response.output if getattr(obj, "type", None) == "function_call"]

        if not tool_calls:
            break

        for tool_call in tool_calls:
            function_name = tool_call.name
            args = json.loads(tool_call.arguments)

            function = TOOL_FUNCTIONS.get(function_name)
            result = {function_name: function(**args)}

            history += [{"type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": json.dumps(result)}]
            

    print(f"\nAssistant: {response.output_text}\n")

    user_input = input("User: ")
    history += [{"role": "user", "content": user_input}]