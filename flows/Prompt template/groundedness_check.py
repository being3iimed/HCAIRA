import os
from langchain.prompts import PromptTemplate

# Genrating queries in ReliefWeb Template
groundedness_check = f'''

System:
You are an AI assistant. You will be given the definition of an evaluation metric for assessing the quality of an answer in a question-answering task. Your job is to compute an accurate evaluation score using the provided evaluation metric.
User:
You will be presented with a CONTEXT and an ANSWER about that CONTEXT. You need to decide whether the ANSWER is entailed by the CONTEXT by choosing one of the following rating:
1. 5: The ANSWER follows logically from the information contained in the CONTEXT.
2. 1: The ANSWER is logically false from the information contained in the CONTEXT.
3. an integer score between 1 and 5 and if such integer score does not exists, use 1: It is not possible to determine whether the ANSWER is true or false without further information.

Read the passage of information thoroughly and select the correct answer from the three answer labels. Read the CONTEXT thoroughly to ensure you know what the CONTEXT entails.

Note the ANSWER is generated by a computer system, it can contain certain symbols, which should not be a negative factor in the evaluation.
Independent Examples:
## Example Task #1 Input:
{"CONTEXT": "The Academy Awards, also known as the Oscars are awards for artistic and technical merit for the film industry. They are presented annually by the Academy of Motion Picture Arts and Sciences, in recognition of excellence in cinematic achievements as assessed by the Academy's voting membership. The Academy Awards are regarded by many as the most prestigious, significant awards in the entertainment industry in the United States and worldwide.", "ANSWER": "Oscar is presented every other two years"}
## Example Task #1 Output:
1
## Example Task #2 Input:
{"CONTEXT": "The Academy Awards, also known as the Oscars are awards for artistic and technical merit for the film industry. They are presented annually by the Academy of Motion Picture Arts and Sciences, in recognition of excellence in cinematic achievements as assessed by the Academy's voting membership. The Academy Awards are regarded by many as the most prestigious, significant awards in the entertainment industry in the United States and worldwide.", "ANSWER": "Oscar is very important awards in the entertainment industry in the United States. And it's also significant worldwide"}
## Example Task #2 Output:
5
## Example Task #3 Input:
{"CONTEXT": "In Quebec, an allophone is a resident, usually an immigrant, whose mother tongue or home language is neither French nor English.", "ANSWER": "In Quebec, an allophone is a resident, usually an immigrant, whose mother tongue or home language is not French."}
## Example Task #3 Output:
5
## Example Task #4 Input:
{"CONTEXT": "Some are reported as not having been wanted at all.", "ANSWER": "All are reported as being completely and fully wanted."}
## Example Task #4 Output:
1

Reminder: The return values for each task should be correctly formatted as an integer between 1 and 5. Do not repeat the context.

## Actual Task Input:
{"CONTEXT": {{context}}, "ANSWER": {{answer}}}

Actual Task Output:'''
groundedness_check_prompt = PromptTemplate.from_template(groundedness_check)

# print(create_reliefWeb_query_prompt.format(context='Disaster', answer='hum'))