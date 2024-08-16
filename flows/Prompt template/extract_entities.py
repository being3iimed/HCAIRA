import os
from langchain.prompts import PromptTemplate

# Genrating queries in ReliefWeb Template
extract_entities = f'''

system:
Your task is to find entities from the given text content.
Entities should one of the following types: disaster_type, location
You should only return the entity list as a JSON record in the following format:

[
    {
       "entity_type": "<ENTITY TYPE>",
       "entity": "<ENTITY>"
    }
    ... etc
]

If there are no entities, return an empty list.

Extract the entities for this text:

{{text}}
'''
extract_entities_prompt = PromptTemplate.from_template(extract_entities)

# print(extract_entities_prompt.format(text='nothing'))