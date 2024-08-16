import os
from langchain.prompts import PromptTemplate

# Generating queries in ReliefWeb Template
answer_question = f'''
system:
You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question.
You always provide your sources when answering a question, providing the report name, link, and quoting the relevant information.

{{reliefweb_data}}

user:
{{question}}
'''

answer_question_prompt = PromptTemplate.from_template(answer_question)

print(answer_question_prompt.format(question='nothing', reliefweb_data='fun'))
