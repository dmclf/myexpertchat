"""
Streamlit frontend that displays a text box to enter questions on the bottom of the page. #
The questions and answers are then displayed as a chat history on the page.
"""


import streamlit as st

from myexpertchat.rag import get_answer_from_rag

st.set_page_config(page_title="MyExpertChat")
st.title("MyExpertChat")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message MyExpertChat..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"MyExpertChat: {get_answer_from_rag(question=prompt)}"

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
