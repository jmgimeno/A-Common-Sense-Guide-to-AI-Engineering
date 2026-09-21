import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from llm_tools import read_webpage, search_web, create_audio
import requests
from bs4 import BeautifulSoup


load_dotenv()
llm = OpenAI()
google_api_key = os.getenv("GOOGLE_API_KEY")
search_engine_id = os.getenv("SEARCH_ENGINE_ID")

research = []
previous_web_queries = []

def llm_response(prompt, tools):
    response = llm.responses.create(
        model="gpt-5-mini",
        tools=tools,
        input=prompt
    )
    return response

def generate_web_query(podcast_description):
    web_query = llm.responses.create(
        model="gpt-5-mini",
        input=f"""You are doing research for a podcast, whose details are: 
        <details>{podcast_description}</details> Generate a Google web
        search query to help do research for this podcast.
        
        <instructions>
        Ensure that your web search query is different than any of the past 
        queries made: <old_query_list>{previous_web_queries}</old_query_list>.
        The web search query should be specific and succinct, no more than 6
        words. For example, if the podcast topic is about the latest news
        in Iceland, your query would be simply: Iceland news
        </instructions>
        Generate the web query now:"""
    )
    # Save web query in global previous_web_queries variable so we don't 
    # ever repeat the same search again:
    previous_web_queries.append(web_query.output_text)
    return web_query.output_text

def extract_text(urls, podcast_description):
    for url in urls:
        webpage_text = read_webpage(url)
        extracted_text = llm.responses.create(
            model="gpt-5-mini",
            input=f"""You are doing research for a podcast, whose details 
            are: <details>{podcast_description}</details>
            Extract whatever relevant information you can from this info  
            you've found on the web: <webpage>{webpage_text}</webpage>. 
            Just include the extracted text and nothing else in your
            response. Generate the extracted text now:"""
        )
        research.append(extracted_text.output_text)

def has_sufficient_research(podcast_description):
    sufficient_research = llm.responses.create(
        model="gpt-5-mini",
        input=f"""You are doing research for a podcast, whose details are: 
        <details>{podcast_description}</details>. Here is the research you 
        have from the web so far: <research>{research}</research>. Do you
        feel that you have enough info to create a fact-based podcast
        based on this research with the information you have so far?
        Keep in mind the desired length of the podcast.
        Respond with either: True/False
        """
    )
    return sufficient_research.output_text

def write_podcast_script(podcast_description):
    script = llm.responses.create(
        model="gpt-5-mini",
        input=f"""You are a podcast scriptwriter, creating scripts for
        news-based and explainer podcasts. The podcast should be based on 
        real facts and web research. As such, do not create any fictional 
        information for the podcast. Only use what you find based on your 
        web research.
        
        Here are the details of what the podcast should be: 
        <details>{podcast_description}</details> Here is the research you 
        should use to produce the script: <research>{research}</research>
        
        The script is read by a single host in a news-like style. Do not 
        create music or the like. Only create the words to be spoken by 
        the host. Create the script now:"""
    )
    return script.output_text

# The main assembly line:
def initiate_podcast(podcast_description):
    # Generate a web query based on podcast description:
    web_query = generate_web_query(podcast_description)
    # Peform a Google search based on the web query:
    urls = search_web(web_query)

    # Read each url's web page and extract relevant text, storing 
    # it in the global variable called research:
    extract_text(urls, podcast_description)

    # Check whether we have enough research to create podcast:
    if has_sufficient_research(podcast_description) == "False":
        # If not enough research, we recursively call initiate_podcast 
        # to continue research:
        initiate_podcast(podcast_description)      

    # Write podcast script based on research:
    podcast_script = write_podcast_script(podcast_description)
    # Convert podcast script to mp3:
    create_audio(podcast_script)
    return True

TOOLS = [
    {
        "type": "function",
        "name": "initiate_podcast",
        "description": """Generates an audio podcast as a file
                       called podcast.mp3""",
        "parameters": {
            "type": "object",
            "properties": {
                "podcast_description": {
                    "type": "string",
                    "description": """A description of what type of podcast
                                   the user wishes to create, including 
                                   topic and length""",
                }
            },
            "required": ["podcast_description"],
        },
    },
]

TOOL_FUNCTIONS = {"initiate_podcast": initiate_podcast}

print(f"Assistant: What podcast would you like me to create?\n")
user_input = input("User: ")
history = [
    {"role": "developer", "content": """You are a podcast producer, creating 
    news-based and explainer podcasts for people on any topic they choose.
    Today's date is {date.today().strftime("%B %d, %Y")}.
     
    Here is the plan you should follow step by step to create a podcast:
    <plan>
    1. When the user describes the podcast they want, do not proceed to the
    next step until you've obtained the following information:
        * The topic of the podcast.
        * How long the podcast should be. (For example, five minutes long.)
    However, do not ask the user about the podcast style. Assume that the 
    podcast style is a single host reporting news and insight.
    2. Next, create a simple summary describing the type of podcast the user
    wants. Ensure that this summary includes the desired time length of the
    podcast. For example, the summary might be: "A 3-minute podcast on the
    latest news, insights, and updates in the field of quantum physics"
    3. You have access to an initiate_podcast tool. Your next step is
    to call the initiate_podcast tool, passing along your summary to it.
    </plan>
    """},
    {"role": "assistant", "content": "How can I help you today?"},
    {"role": "user", "content": user_input}
]

while user_input != "exit":  # Main conversation loop
    while True:  ## the agent loop
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