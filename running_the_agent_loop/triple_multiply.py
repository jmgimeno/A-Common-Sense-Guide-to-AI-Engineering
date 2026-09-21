import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

def llm_response(prompt, tools):
    response = llm.responses.create(
        model="gpt-5-mini",
        tools=tools,
        input=prompt
    )
    return response

def multiply_two_numbers(first_number, second_number):
    product = int(first_number) * int(second_number)
    print(f"MULTIPLY: {product}")
    return product

tools = [
    {
        "type": "function",
        "name": "multiply_two_numbers",
        "description": "Multiply two numbers to get a product.",
        "parameters": {
            "type": "object",
            "properties": {
                "first_number": { "type": "integer" },
                "second_number": { "type": "integer" },
            },
            "required": ["first_number", "second_number"],
        },
    },
]

print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": """You are a helpful AI assistant. If you ever need to 
    multiply two numbers, DO NOT attempt to answer with your internal knowledge. 
    Instead, use your multiply_two_numbers tool."""},
    {"role": "assistant", "content": "How can I help you today?"}
]

while user_input != "exit":
    history += [{"role": "user", "content": user_input}]

    response = llm_response(history, tools)
    history += response.output
    tool_calls = [obj for obj in response.output \
                  if getattr(obj, "type", None) == "function_call"]

    while tool_calls:  ## the "agent loop"
        for tool_call in tool_calls:
            function_name = tool_call.name
            args = json.loads(tool_call.arguments)

            if function_name == "multiply_two_numbers":
                result = {"multiply_two_numbers": multiply_two_numbers(**args)}
                
                history += [{"type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(result)}]
                
                response = llm_response(history, tools)
                history += response.output
                tool_calls = [obj for obj in response.output \
                              if getattr(obj, "type", None) == "function_call"]
                

    print(f"\nAssistant: {response.output_text}\n")

    history += [
        {"role": "assistant", "content": response.output_text},
    ]

    user_input = input("User: ")