import os
from langchain.prompts import PromptTemplate

# Genrating queries in ReliefWeb Template
summarize_basic = f'''

system:

You are a humanitarian researcher who needs produces accurate and consise summaries of latest news

========= TEXT BEGIN =========

{{text}}

========= TEXT END =========

Using the output from reliefweb above, write a summary of the article.
Be sure to capture any numerical data, and the main points of the article.
Be sure to capture any organizations or people mentioned in the article.
'''
summarize_basic_prompt = PromptTemplate.from_template(summarize_basic)

# print(summarize_basic_prompt.format(text='nothing'))

  