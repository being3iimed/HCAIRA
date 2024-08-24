# app.py
import streamlit as st
import warnings
from model import initialize_model, initial_prompt, chain_prompt  # Import functions from model.py

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

# Initialize session state
if "toast_shown" not in st.session_state:
    st.session_state["toast_shown"] = False
if not st.session_state["toast_shown"]:
    st.toast("The snowflake data retrieval is disabled for now.", icon="👋")
    st.session_state["toast_shown"] = True

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("Enter your Mistral API Key", type="password")

if st.sidebar.button("Submit API Key"):
    if api_key:
        st.session_state["api_key"] = api_key
        st.sidebar.success("API Key submitted! You can now start asking questions.")
    else:
        st.sidebar.error("Please enter your Mistral API Key.")

if st.sidebar.button("Reset Chat"):
    st.session_state["chat_history"] = []

# Main chat interface
if "api_key" in st.session_state:
    st.header("Chat History")

    for chat in st.session_state["chat_history"]:
        st.markdown(f"<div style='text-align: right; color: blue;'><strong>User:</strong> {chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: left; color: green;'><strong>Assistant:</strong> {chat['assistant']}</div>", unsafe_allow_html=True)
        st.write("---")

    query = st.text_input("Type your question here and press Enter to submit", key="query_input", label_visibility="hidden")

    if st.button("Submit Question", use_container_width=True):
        if query:
            llm_with_tools = initialize_model(st.session_state["api_key"])
            response = {}

            if len(st.session_state["chat_history"]) == 0:
                response = initial_prompt(query, llm_with_tools)
            else:
                previous_output = st.session_state["chat_history"][-1]['assistant']
                response = chain_prompt(previous_output, query, llm_with_tools)

            if isinstance(response, dict):
                st.session_state["chat_history"].append(response)
                st.markdown(f"<div style='text-align: left; color: green;'><strong>Assistant:</strong> {response['assistant']}</div>", unsafe_allow_html=True)
            else:
                st.write(f"**Assistant:** {response}")
else:
    st.warning("Please submit your API Key in the sidebar to start interacting with the assistant.")
