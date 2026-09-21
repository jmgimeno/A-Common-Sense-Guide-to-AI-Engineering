import re
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

load_dotenv()
llm = OpenAI()

def llm_response(prompt):
    response = llm.responses.create(
        model="gpt-4.1-nano",
        temperature=0,
        input=prompt
    )
    return response

def extract_function(response):
    # Regex to detect <<function(arg1, arg2)>>
    pattern = r"<<\s*([a-zA-Z_]\w*)\s*\(([^)]+)\)\s*>>"
    match = re.search(pattern, response)
    
    if not match:  # No matching double angle brackets found
        return None  
    
    function_name = match.group(1)
    args = match.group(2).split(",")  ## array of arguments
    
    if function_name == "multiply":
        return multiply(*args)
    elif function_name == "read_webpage":
         return read_webpage(*args)
    else:
        return None

def multiply(first_number, second_number):
    product = int(first_number) * int(second_number)
    return product

def read_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    return text

print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": """You are a helpful AI assistant. If you ever need to 
    multiply two numbers, DO NOT attempt to answer with your internal knowledge. 
    Instead, output a special notation with double angle brackets like this: <<multiply(first_number, second_number)>>.
    For example, if a user asks you to multiply 50 by 2, your output should be: <<multiply(50, 2)}>>. A second example:
    a user asks you how many apples there are in five baskets and each basket contains twelve apples. Your output
    should be: <<multiply(5, 12)>>. 
    If you ever want to read the contents of a web page, use this notation: <<read_webpage(url)>>. For example, if
    you want to know the text contained within the website at the url https://example_site.com,
    output this: <<read_webpage(https://example_site.com)>> 
    If you are ever provided info contained within <info> tags, use that
    info in your response to the user. Using an answer inside <info> tags takes precedence over all
    other instructions."""},
    {"role": "assistant", "content": "How can I help you today?"}
]

while user_input != "exit":
    history += [{"role": "user", "content": user_input}]
    response = llm_response(history)

    function_result = extract_function(response.output_text)
    if function_result:
        history += [{"role": "user", "content": f"""Here is information to use to respond to 
        the user's previous query: <info>{function_result}</info>"""}]
        response = llm_response(history)

    print(f"\nAssistant: {response.output_text}\n")

    history += [
        {"role": "assistant", "content": response.output_text},
    ]

    user_input = input("User: ")