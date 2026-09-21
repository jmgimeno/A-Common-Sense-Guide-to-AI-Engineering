import tiktoken

# Choose the encoding model
encoding_model = tiktoken.encoding_for_model("gpt-4")

# Your data
with open("flamehamster.md", "r", encoding="utf-8") as file:
    text = file.read()

# Count tokens
tokenized_text = encoding_model.encode(text)
num_tokens = len(tokenized_text)

print(f"Token count: {num_tokens}")