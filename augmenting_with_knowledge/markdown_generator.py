from docling.document_converter import DocumentConverter

source = "https://archive.flossmanuals.net/_booki/firefox/firefox.pdf"
converter = DocumentConverter()
doc = converter.convert(source).document

with open("flamehamster.md", "w", encoding="utf-8") as f:
    f.write(doc.export_to_markdown())