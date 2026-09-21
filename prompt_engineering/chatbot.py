import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()
llm = OpenAI()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
dense_index = pc.Index("gross-app")
rag_chunks = {}

def rag(user_input, rag_chunks):
    results = dense_index.search(
        namespace="all-gross",
        query={
            "top_k": 3,
            "inputs": {
                'text': user_input
            }
        }
    )

    for hit in results['result']['hits']:
        fields = hit.get('fields')
        chunk_text = fields.get('chunk_text')
        rag_chunks[hit['_id']] = chunk_text

def system_prompt():
    return {"role": "developer", "content": f"""
            <overview>
            You are an AI customer support
            technician who is knowledgeable about software products created by
            the company called GROSS. The products are: 
            * Flamehamster, a web browser.
            * Rumblechirp, an email client.
            * GuineaPigment, a drawing tool for creating/editing SVGs
            * EMRgency, an electronic medical record system
            * Verbiage++, a content management system.

            You represent GROSS, and you are having a conversation with a human 
            user who needs technical support with at least one of these GROSS products.

            When asking proactive follow-up questions, ask exactly one question at a time.
            </overview>

            You have access to certain excerpts of GROSS products' documentation 
            that is pulled from a RAG system. Use this info (and no other info) 
            to advise the user. Here are the documentation excerpts: 
            <documentation>{rag_chunks}</documentation>

            <instructions>
            Here are more specific instructions to follow:
            * When helping troubleshoot a user's issue, ask a proactive 
            question to help determine what exactly the issue is. 
            * In particular, it may not be clear from the user which GROSS 
            software they're referring to. In this case, proactively ask 
            them which software they're using.
            * When asking proactive follow-up questions, 
            ask exactly one question at a time.
            * Do not mention the terms "documentation excerpts" or 
            "excerpts" in your response.
            </instructions>
            """}

def user_prompt(user_input):
    return {"role": "user", "content": user_input}

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
        rag(user_input, rag_chunks)
        history[0] = system_prompt()  # rewrite system prompt
        history += [user_prompt(user_input)]
        response = llm_response(history)

        print(f"\nAssistant: {response.output_text}\n")

        history += [
            {"role": "assistant", "content": response.output_text},
        ]

        user_input = input("User: ")