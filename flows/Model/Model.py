import os
import api
import streamlit as st
from langchain.chains import LLMChain
from langchain_core.tools import Tool
from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate

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

# Function to check if the query is disaster-related
def is_disaster_related(query):
    disaster_keywords = ["disaster", "earthquake", "flood", "hurricane", "tsunami", "wildfire", "storm", "landslide", "cold wave"]
    return any(keyword in query.lower() for keyword in disaster_keywords)

# Function to infer the real intent of the user query
def infer_user_intent(query, chat_history):
    extract_query_prompt = f"""
    system:
    You are an AI assistant reading the transcript of a conversation between an AI and a human. Given an input question and conversation history, infer user real intent.

    The conversation history is provided just in case of a context (e.g. "What is this?" where "this" is defined in previous conversation).

    Return the output as a query that could be used in a search engine

    user:
    Conversation history:
    {chat_history}

    Output: {query}
    """
    # Assume that there is a function to call the LLM model
    refined_query = llm_with_tools.invoke(input=extract_query_prompt).content
    return refined_query

# Function to fetch data using the tool
def fetch_disaster_data(query):
    data = api.get_data(query)
    return api.convent_string_to_dictionary(data)

# First prompt function
def initial_prompt(query, llm_with_tools, chat_history):
    # Infer user intent from query
    refined_query = infer_user_intent(query, chat_history)

    # Check if the refined query is disaster-related
    if is_disaster_related(refined_query):
        # Fetch data using the tool
        schema = fetch_disaster_data(refined_query)

        # Define the prompt template
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system",
                 "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. "
                 "You always provide your sources when answering a question. {relief_web_data}."),
                ("user", "{query}"),
            ]
        )

        # Format the first query prompt
        formatted_prompt = prompt_template.format_prompt(query=refined_query, relief_web_data=schema)

        # Invoke the model for the first query
        response = llm_with_tools.invoke(input=formatted_prompt)

        return response.content
    else:
        return "The information provided is not related to disasters. Please ask a question specifically about disasters or humanitarian crises."

# Second prompt function (for follow-up queries using previous context)
def chain_prompt(previous_output, query, llm_with_tools, chat_history):
    # Infer user intent from query
    refined_query = infer_user_intent(query, chat_history)

    # Check if the refined query is disaster-related
    if is_disaster_related(refined_query):
        # Fetch data using the tool
        schema = fetch_disaster_data(refined_query)

        # Define the prompt template for the second query
        chain_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system",
                 "You are a helpful assistant. Using the previous output and any other relevant data, answer the user's "
                 "new question."),
                ("user", "{previous_output}\nUser's question: {query}")
            ]
        )

        # Format the second query prompt
        formatted_chain_prompt = chain_prompt_template.format_prompt(previous_output=previous_output, query=refined_query)

        # Invoke the model for the second query
        chain_response = llm_with_tools.invoke(input=formatted_chain_prompt)
        return chain_response.content
    else:
        return "The information provided is not related to disasters. Please ask a question specifically about disasters or humanitarian crises."

# Streamlit app setup
st.title("AI Assistant")

# Sidebar for API Key input
st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("Enter your Mistral API Key", type="password")

if st.sidebar.button("Submit API Key"):
    if api_key:
        st.session_state["api_key"] = api_key
        st.sidebar.success("API Key submitted! You can now start asking questions.")
    else:
        st.sidebar.error("Please enter your Mistral API Key.")

# Main chat interface
if "api_key" in st.session_state:
    # Chat history
    st.header("Chat History")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for chat in st.session_state["chat_history"]:
        st.write(f"**User:** {chat['user']}")
        st.write(f"**Assistant:** {chat['assistant']}")
        st.write("---")

    # Input for the user's question
    query = st.text_input("Type your question here and press Enter to submit", key="query_input")

    # Handle the query submission
    if st.button("Submit Query"):
        if query:
            llm_with_tools = initialize_model(st.session_state["api_key"])
            if not st.session_state["chat_history"]:
                response = initial_prompt(query, llm_with_tools, st.session_state["chat_history"])
            else:
                last_response = st.session_state["chat_history"][-1]["assistant"]
                response = chain_prompt(last_response, query, llm_with_tools, st.session_state["chat_history"])
            
            st.session_state["chat_history"].append({"user": query, "assistant": response})
            st.write(f"**Assistant:** {response}")

# If no API key has been submitted
else:
    st.warning("Please submit your API Key in the sidebar to start interacting with the assistant.")
