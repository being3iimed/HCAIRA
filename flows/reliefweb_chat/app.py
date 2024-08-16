import streamlit as st
import json
from process_output import process_output

# Streamlit app setup
st.title("ReliefWeb Chat Flow Processor")

# User input fields
user_question = st.text_input("User Question")
query_entities = st.text_input("Query Entities")
rweb_query = st.text_input("ReliefWeb Query")
rweb_results = st.text_area("ReliefWeb Results (JSON format)")
llm_summary_result = st.text_area("LLM Summary Result (JSON format)")
refs = st.text_area("References (JSON format)")
llm_question_result = st.text_area("LLM Question Result")
content_safety_result = st.text_input("Content Safety Result", "Accept")

# Process the input and display output when the button is clicked
if st.button("Process"):
    if user_question and rweb_results and llm_summary_result and refs and llm_question_result:
        try:
            # Convert JSON string inputs to dictionaries
            rweb_results_json = json.loads(rweb_results)
            refs_json = json.loads(refs)
            llm_summary_result_json = json.loads(llm_summary_result)

            # Process the output using the function
            output = process_output(
                user_question=user_question,
                query_entities=query_entities,
                rweb_query=rweb_query,
                rweb_results=json.dumps(rweb_results_json),
                llm_summary_result=json.dumps(llm_summary_result_json),
                refs=json.dumps(refs_json),
                llm_question_result=llm_question_result,
                content_safety_result=content_safety_result,
            )

            # Display the output
            st.subheader("Processed Output")
            st.json(output)

        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON input: {e}")
    else:
        st.error("Please fill in all required fields.")
