import json
from datetime import date
from llm_tools import read_webpage, search_web, create_audio
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
llm = OpenAI()

def llm_response(prompt, tools):
    response = llm.responses.create(
        model="gpt-5-mini",
        tools=TOOLS,
        input=prompt
    )
    return response

TOOLS = [
    {
        "type": "function",
        "name": "search_web",
        "description": """Searches the web based on a query and 
                       retrieves an array of relevant URLs.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query of the web search",
                }
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "read_webpage",
        "description": "Accesses a webpage and obtains its text.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage",
                }
            },
            "required": ["url"],
        },
    },
    {
        "type": "function",
        "name": "create_audio",
        "description": """Uses text-to-speech technology to convert a 
                       podcast script (string) into an audio mp3 podcast 
                       named podcast.mp3.""",
        "parameters": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "A podcast script read by a single host",
                }
            },
            "required": ["script"],
        },
    },
]

TOOL_FUNCTIONS = {
    "search_web": search_web,
    "read_webpage": read_webpage,
    "create_audio": create_audio,
}

print(f"Assistant: How can I help you today?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": """You are a podcast producer, creating news-based and explainer
    podcasts for people on any topic they choose. The podcast should be based on real facts and web research. As such, do not create any fictional information for the podcast. 
    Only use what you find based on your web research.
    Today's date is {date.today().strftime("%B %d, %Y")}.

    You have access to several specialized tools. Here are your tools:
    <tools>
    * With the search_web tool, you have the ability to search the web based on a query and retrieve urls of web pages relevant to that query. This is especially useful for searching for current information and information you don't possess in your internal knowledge.
    * With the read_webpage tool, you have the ability to read the text from a webpage of any given url. This is a useful tool to use in conjunction with the search_web tool. That is, the search_web tool retrieves urls, and the read_webpage tool can read the text contained at those web pages.
    * With the create_audio tool, you can convert a podcast script text into an audio mp3 podcast.
    </tools>
    
    Here is the plan you should follow step by step to create a podcast:
    <plan>
    1. When the user descibes the podcast they want, do not create the podcast until you've obtained the following information:
          * The topic of the podcast.
          * How long the podcast should be. (For example, five minutes long.)
       However, do not ask the user about the podcast style. Assume that the podcast style is a single host reporting news and insight.
    2. Next, use the search_web tool for a single query to find webpage URLs that are relevant to the podcast topic. This will return an array of URLs. Do not call search_web multiple times at once. After calling it a single time, move on to the next step.
    3. Next, use the read_webpage tool on each URL to read the information contained within those web pages.
    4. After reading the content of all the web pages, determine whether you have enough relevant factual material to fill a podcast of the user's desired length.
    5. If you do not have enough relevant material, go back to Step #2 to use the search_web tool again, this time on a new web query than you've searched previously.
    6. If you have enough relevant material, you should then use the create_audio tool to create the podcast, which will create an mp3 file called podcast.mp3.
    </plan>
    """},
    {"role": "user", "content": user_input}
]

while user_input != "exit":  # main conversation loop

    while True:  # the agent loop
        response = llm_response(history, TOOLS)
        history += response.output
        tool_calls = [obj for obj in response.output if \
                      getattr(obj, "type", None) == "function_call"]

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

    user_input = input("User: ")
    history += [{"role": "user", "content": user_input}]