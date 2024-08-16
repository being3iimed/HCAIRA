import os
from langchain.prompts import PromptTemplate

# Genrating queries in ReliefWeb Template
answer_question = f'''
system:
You are a helpful assistant. Using the output from a query to reliefweb, anser the user's question.
You always provide your sources when answering a question, providing the report name, link and quote the relevant information.

{{reliefweb_data}}

{% for item in chat_history %}
user:
{{item.inputs.question}}
assistant:
{{item.outputs.answer}}
{% endfor %}

user:
{{question}}'''
answer_question_prompt = PromptTemplate.from_template(answer_question)