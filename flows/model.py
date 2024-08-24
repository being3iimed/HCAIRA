# model.py
import os
import api
from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_mistralai import ChatMistralAI

# Initialize the model and set up the environment
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

# First prompt function
def initial_prompt(query, llm_with_tools):
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question."
             "You always provide your sources when answering a question. Please only answer questions related to "
             "humanitarian crises or aid. Do not leave an answer empty and ensure content is in human-readable format."
             "\n{relief_web_data}."),
            ("user", "{query}"),
        ]
    )

    data = api.get_data(query)
    if not data or len(data) == 0 or "[]" in data:
        return "Sorry, I cannot help you with your query."

    schema = api.convent_string_to_dictionary(data)
    formatted_prompt = prompt_template.format_prompt(query=query, relief_web_data=schema)
    response = llm_with_tools.invoke(input=formatted_prompt)
    return {"user": query, "assistant": response.content}

# Chain prompt function
def chain_prompt(previous_output, query, llm_with_tools):
    chain_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question."
             "You always provide your sources when answering a question. Answer questions related to "
             "humanitarian crises or aid. Please do not leave an answer empty. "
             "Using the previous output and any other relevant data, answer the user's "
             "new question in human-readable format."
             "\n{relief_web_data}."),
            ("user", "{previous_output}\nUser's question: {query}")
        ]
    )

    data = api.get_data(query)
    if not data or len(data) == 0 or "[]" in data:
        return "Sorry, I cannot help you with your query."

    schema = api.convent_string_to_dictionary(data)
    formatted_chain_prompt = chain_prompt_template.format_prompt(previous_output=previous_output, query=query, relief_web_data=schema)
    chain_response = llm_with_tools.invoke(input=formatted_chain_prompt)
    return {"user": query, "assistant": chain_response.content}
