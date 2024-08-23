import os
import api
import streamlit as st
from langchain.chains import LLMChain
from langchain_core.tools import Tool
from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate
import warnings

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

# Function to check if a new query can be answered using previous responses
def can_answer_from_previous(query, previous_responses):
    # Check if the query is about the same topic as previous responses
    keywords_in_previous = [resp['query_keywords'] for resp in previous_responses]
    current_keywords = extract_keywords(query)  # Implement a keyword extraction method

    for keywords in keywords_in_previous:
        if set(current_keywords).intersection(set(keywords)):
            # Return True if the current query's keywords overlap with any previous response keywords
            return True, [resp['assistant'] for resp in previous_responses if set(keywords).intersection(set(current_keywords))][0]
    return False, None

def extract_keywords(text):
    # Simple keyword extraction (can be replaced with a more sophisticated method)
    return text.lower().split()

# Function to handle user queries and fetch data from ReliefWeb tool if necessary
def handle_query(query, llm_with_tools, previous_responses):
    # Check if the query can be answered from previous responses
    can_answer, previous_answer = can_answer_from_previous(query, previous_responses)
    
    if can_answer:
        return previous_answer

    # If no answer is found in previous responses, fetch new data using the ReliefWeb tool
    data = api.get_data(query)
    schema = api.convent_string_to_dictionary(data)

    # Define the prompt template
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. "
             "You always provide your sources when answering a question. {relief_web_data}."),
            ("user", "{query}"),
        ]
    )

    # Format the prompt with the fetched data
    formatted_prompt = prompt_template.format_prompt(query=query, relief_web_data=schema)

    # Invoke the model with the formatted prompt
    response = llm_with_tools.invoke(input=formatted_prompt)

    # Append fetched data to chat history
    previous_responses.append({"user": query, "assistant": response.content, "query_keywords": extract_keywords(query), "fetched_data": schema})

    return response.content

# Streamlit app setup
warnings.filterwarnings("ignore")

# Gradient text styling
gradient_text_html = """
<style>
.gradient-text {
    font-weight: bold;
    background: -webkit-linear-gradient(left, red, orange);
    background: linear-gradient(to right, red, orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline;
    font-size: 3em;
}
</style>
<div class="gradient-text">Humanitarian Crises AI Report Assistant</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)
st.caption("Talk your way through data")

# Chatbot description
st.write("**What does this chatbot do?**")
st.write("This chatbot helps you find and understand information about humanitarian crises. "
         "It queries the ReliefWeb API to fetch up-to-date data on various crises and provides insightful responses. "
         "Feel free to ask questions about different humanitarian emergencies, and the assistant will provide you with relevant data and context.")

if "toast_shown" not in st.session_state:
    st.session_state["toast_shown"] = False

if not st.session_state["toast_shown"]:
    st.toast("The snowflake data retrieval is disabled for now.", icon="👋")
    st.session_state["toast_shown"] = True

st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("Enter your Mistral API Key", type="password")

if st.sidebar.button("Submit API Key"):
    if api_key:
        st.session_state["api_key"] = api_key
        st.sidebar.success("API Key submitted! You can now start asking questions.")
    else:
        st.sidebar.error("Please enter your Mistral API Key.")

# Sidebar for reset and DDL
if st.sidebar.button("Reset Chat"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["chat_history"] = []

# Check if API key is provided
if "api_key" in st.session_state:
    st.header("Chat History")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display chat history with user and assistant messages formatted
    for chat in st.session_state["chat_history"]:
        st.markdown(f"<div style='text-align: right; color: blue;'><strong>User:</strong> {chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: left; color: green;'><strong>Assistant:</strong> {chat['assistant']}</div>", unsafe_allow_html=True)
        st.write("---")

    # Place the user input box at the bottom of the page
    query = st.text_input("Type your question here and press Enter to submit", key="query_input", label_visibility="hidden")

    if st.button("Submit Question", use_container_width=True):
        if query:
            llm_with_tools = initialize_model(st.session_state["api_key"])
            response = handle_query(query, llm_with_tools, st.session_state["chat_history"])
            
            st.session_state["chat_history"].append({"user": query, "assistant": response})
            st.write(f"<div style='text-align: left; color: green;'><strong>Assistant:</strong> {response}</div>", unsafe_allow_html=True)

else:
    st.warning("Please submit your API Key in the sidebar to start interacting with the assistant.")
