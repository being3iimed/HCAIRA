import os
from langchain.prompts import PromptTemplate

# Genrating queries in ReliefWeb Template
create_reliefWeb_query = f'''
system:
You generate queries to run on Reliefweb in order to extract data about reports and disasters. 
You build these from a list of entities provided by the user.
Your output is a string

EXAMPLE:

input:

[
    {
       "entity_type": "location",
       "entity": "sudan"
    },
    {
       "entity_type": "disaster_type",
       "entity": "conflict"
    },
    {
       "entity_type": "year",
       "entity": "2024"
    }

    ... etc
]
output:
Sudan conflict 2024

user:
{{question}}

'''
create_reliefWeb_query_prompt = PromptTemplate.from_template(create_reliefWeb_query)
# print(create_reliefWeb_query_prompt.format(question='nothing'))