import os
from langchain.prompts import PromptTemplate

# Directory containing Jinja2 template files
template_directory = "PromptTemplate"

# Load multiple Jinja2 templates
templates = {}
for filename in os.listdir(template_directory):
    if filename.endswith(".jinja2"):
        file_path = os.path.join(template_directory, filename)
        # Load each template into a PromptTemplate instance
        templates[filename] = PromptTemplate.from_template(file_path, template_format="jinja2")
