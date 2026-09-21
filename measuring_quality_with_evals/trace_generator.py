import csv
from chatbot import rag, system_prompt, user_prompt, llm_response

input_file = 'queries.csv'
output_file = 'traces.csv'

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    writer.writerow(["Query Topic", "User Query", "History", "AI Response"])

    for row_index, row in enumerate(reader):
        query_topic = row[0]
        user_input = row[1]
        history = [
            system_prompt(),
            {"role": "assistant", "content": "How can I help you today?"}
        ]

        documentation = rag(user_input)
        history += [user_prompt(user_input, documentation)]
        response = llm_response(history)

        writer.writerow([query_topic, user_input,
                         str(history), response.output_text])
        print(f"query {row_index} completed")