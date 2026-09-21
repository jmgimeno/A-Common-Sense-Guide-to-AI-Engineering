import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
llm = OpenAI()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")

def rag(user_input):
    results = dense_index.search(
        namespace="all-gross",
        query={
            "top_k": 3,
            "inputs": {
                'text': user_input
            }
        }
    )

    documentation = ""
    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        documentation += chunk_text

    return documentation

def system_prompt():
    return {"role": "developer", "content": """You are an AI customer support
    technician who is knowledgeable about software products created by
    the company called GROSS. The products are: 
    * Flamehamster, a web browser.
    * Rumblechirp, an email client.
    * GuineaPigment, a drawing tool for creating/editing SVGs
    * EMRgency, an electronic medical record system
    * Verbiage++, a content management system."""}

def user_prompt(user_input, documentation):
    return {"role": "user", 
            "content": f"""Here are excerpts from the official GROSS product
            documentation: {documentation}. Use whatever 
            info from the above documentation excerpts (and no other info)
            to answer the following query: {user_input}"""}

def llm_response(prompt):
    response = llm.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        input=prompt
    )
    return response

if __name__ == "__main__":
    print(f"Assistant: How can I help you today?\n")
    user_input = input("User: ")
    history = [
        system_prompt(), 
        {"role": "assistant", "content": "How can I help you today?"}
    ]

    while user_input != "exit":
        documentation = rag(user_input)
        history += [user_prompt(user_input, documentation)]
        response = llm_response(history)

        print(f"\nAssistant: {response.output_text}\n")

        history += [
            {"role": "assistant", "content": response.output_text},
        ]

        user_input = input("User: ")