import json
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3

load_dotenv()
llm = OpenAI()

def llm_response(prompt, tools):
    response = llm.responses.create(
        model="gpt-4.1-nano",
        tools=tools,
        input=prompt
    )
    return response

def query_db(query):
    conn = sqlite3.connect("gross.db")
    cursor = conn.cursor()
    cursor.execute(query)

    # If it's a SELECT query, fetch results
    if query.strip().lower().startswith("select"):
        data = cursor.fetchall()
    else:
        # For INSERT, UPDATE, DELETE, etc.
        conn.commit()
        data = {"rows_affected": cursor.rowcount}

    return data

TOOLS = [
    {
        "type": "function",
        "name": "query_db",
        "description": "Runs SQL search queries on a SQLite database.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A SQL query",
                }
            },
            "required": ["query"],
        },
    },
]

TOOL_FUNCTIONS = {
    "query_db": query_db
}

db_schema = """
    CREATE TABLE Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE Orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10, 2),
        status TEXT DEFAULT 'paid',
        payment_method TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
    );
"""

logged_in_user = "roy62@example.net"
print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": f"""You are a customer support specialist
    for GROSS, a software product company. You have access to a SQLite 
    database containing info about customers and the products they've ordered.

    You may only manage data relating to the currently
    logged-in user: {logged_in_user}. Providing or updating info 
    relating to any other customer would be a MAJOR PRIVACY BREACH!

    Here was the code used to create the SQLite database schema:

    <schema>{db_schema}</schema>

    You have access to several specialized tools. Here are your tools:
    <tools>
    * Your query_db tool allows you to run any SQL query against the company
    database. You need to generate your own SQL query and pass it to the 
    query_db tool in order to execute it.
    </tools>
    """},
    {"role": "assistant", "content": "How can I help you today?"},
    {"role": "user", "content": user_input}
]

while user_input != "exit":

    while True:  ## the "agent loop"
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
    history += [{"role": "user", "content": user_input}]