from docling.document_converter import DocumentConverter

converter = DocumentConverter()
sources = {
    "https://archive.flossmanuals.net/_booki/inkscape/inkscape.pdf": "inkscape.md",
    "https://archive.flossmanuals.net/_booki/thunderbird/thunderbird.pdf": "thunderbird.md",
    "https://archive.flossmanuals.net/_booki/wordpress/wordpress.pdf": "wordpress.md",
    "https://archive.flossmanuals.net/_booki/openmrs-guide/openmrs-guide.pdf": "openmrs.md"
}

for source, filename in sources.items():
    doc = converter.convert(source).document
    with open(filename, "w", encoding="utf-8") as f:
        f.write(doc.export_to_markdown())
    print(f"successfully converted {filename}")