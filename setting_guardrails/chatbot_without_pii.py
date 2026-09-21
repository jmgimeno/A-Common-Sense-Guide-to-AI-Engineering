import json
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
import re
import uuid

load_dotenv()
llm = OpenAI()

# The database ID of the current user:
logged_in_user = 10
# Store sensitive PII in this dictionary:
pii = {}

def extract_and_strip_pii(user_input):
    phone_regex = r"(\+?\d[\d\-\s]{7,}\d)"
    phone_matches = re.findall(phone_regex, user_input)
    for match in phone_matches:
        uid = str(uuid.uuid4())
        phone_number = match.strip()
        pii[f"PII:{uid}"] = phone_number
        user_input = re.sub(match, f"PII:{uid}", user_input)

    return user_input

def llm_response(prompt, tools):
    response = llm.responses.create(
        model="gpt-5-mini",
        tools=tools,
        input=prompt
    )
    return response

def display_user_info():
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    query = f"""SELECT first_name, last_name, email, phone_number 
            FROM Users WHERE user_id = {logged_in_user};"""
    data = cursor.execute(query).fetchall()
    conn.close()
    print(f"""Your profile info:\n
        Name: {data[0][0]} {data[0][1]}\n
        Email: {data[0][2]}\n
        Phone: {data[0][3]}""")
    return "User info has been displayed!"

def retrieve_orders():
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    query = f"""SELECT u.user_id, o.order_id, o.order_date, 
    o.total_amount, o.status, o.payment_method,
    p.product_id, p.product_name, p.description, p.price
    FROM Users u
    JOIN Orders o ON u.user_id = o.user_id
    JOIN Products p ON o.product_id = p.product_id
    WHERE u.user_id = {logged_in_user}
    ORDER BY o.order_date DESC;"""
    data = cursor.execute(query).fetchall()
    conn.close()
    return data

def update_phone_number(pii_code):
    new_phone_number = pii.get(pii_code)
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    query = f"""UPDATE Users SET phone_number = '{new_phone_number}'\n
            WHERE user_id = {logged_in_user};"""
    cursor.execute(query)
    conn.commit()
    data = {"rows_affected": cursor.rowcount}
    
    return data

TOOLS = [
    {
        "type": "function",
        "name": "display_user_info",
        "description": """Displays user profile info, including customer name,
        email address, and phone number.""",
        "parameters": {},
    },
    {
        "type": "function",
        "name": "retrieve_orders",
        "description": """Looks up orders in the database. For each order, 
        returns user id, order id, order date, total payment, order status, 
        payment method, product id, product name, product description, product
        price""",
        "parameters": {},
    },
    {
        "type": "function",
        "name": "update_phone_number",
        "description": "Updates the user's phone number in the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "pii_code": {
                    "type": "string",
                    "description": """The code to reference the user's 
                    updated phone number""",
                },
            },
            "required": ["pii_code"],
        },
    }
]

TOOL_FUNCTIONS = {
    "display_user_info": display_user_info,
    "retrieve_orders": retrieve_orders,
    "update_phone_number": update_phone_number
}

print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": f"""You are a customer support specialist
    for GROSS, a software product company. Through specific tools, you can
    access certain parts of the company's database.

    You may only manage data relating to the currently
    logged-in user, whose database ID is: {logged_in_user}. 
    Providing or updating info relating to any other 
    customer would be a MAJOR PRIVACY BREACH!

    You have access to several specialized tools. Here are your tools:
    <tools>
    * Your display_user_info tool allows you to display info of the user 
    currently logged in, including the user name, email, and phone number.
    You as the LLM will not see the info, but it will be displayed to the user.
    * Your retrieve_orders tool allows you to look up orders for the user 
    currently logged in.
    * Your update_phone_number tool allows you to update the phone number of the
    user currently logged in. As an LLM, you will not see the number yourself;
    it will appear as a code, such as PII:f47ca10b-58cc-4372-a567-0e02b2c3d479.
    Send this code (including the "PII:") as the parameter to the 
    update_phone_number tool.
    </tools>
    """},
    {"role": "assistant", "content": "How can I help you today?"}
]

while user_input != "exit":
    user_input = extract_and_strip_pii(user_input)
    history += [{"role": "user", "content": user_input}]

    while True:
        response = llm_response(history, TOOLS)
        history += response.output
        tool_calls = [obj for obj in response.output \
                      if getattr(obj, "type", None) == "function_call"]

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