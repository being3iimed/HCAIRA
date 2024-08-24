# model.py

import os
from langchain.chains import LLMChain
from langchain_core.tools import Tool
from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate
import api

def initialize_model(api_key):
    os.environ["MISTRAL_API_KEY"] = api_key
    llm = ChatMistralAI(model="mistral-large-latest")

    # Define the tool for querying ReliefWebAPI
    tools = Tool(
        name="ReliefWebAPI",
        func=api.ReliefWebAPIWrapper.run,
        description="Queries the custom API with the user's query"
    )
    llm_with_tools = llm.bind_tools([tools])

    return llm_with_tools

def extract_keywords(text):
    return text.lower().split()

def handle_query(query, llm_with_tools, previous_responses):
    # Directly fetch new data using the ReliefWeb tool, without checking previous responses
    data = api.get_data(query)
    schema = api.convent_string_to_dictionary(data)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. "
             "You always provide your sources when answering a question. {relief_web_data}."),
            ("user", "{query}"),
        ]
    )

    formatted_prompt = prompt_template.format_prompt(query=query, relief_web_data=schema)
    response = llm_with_tools.invoke(input=formatted_prompt)

    # Append fetched data to chat history
    previous_responses.append({"user": query, "assistant": response.content, "query_keywords": extract_keywords(query), "fetched_data": schema})

    return response.content
