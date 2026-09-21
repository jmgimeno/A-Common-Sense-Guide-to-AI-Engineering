import os
import re

def promote_numbered_h2_to_h1(md_text):
    # Regex pattern to match "## <number>. <text>" at the beginning of a line
    pattern = r'(?m)^##\s+(\d+\.\s.+)'
    # Replace with "# <number>. <text>"
    return re.sub(pattern, r'# \1', md_text)

def process_markdown_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".md"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            modified_content = promote_numbered_h2_to_h1(md_content)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(modified_content)

            print(f"Processed: {filename}")

# Example usage
input_folder = "original_files"
output_folder = "data"

process_markdown_files(input_folder, output_folder)
print("All markdown files updated successfully.")