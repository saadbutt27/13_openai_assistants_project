import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import time

# Set your OpenAI's assistant id here
assistant_id = "asst_1t9M5FrwKxR7S0oFyeYJfffr"

# Initialize the OpenAI Client
load_dotenv(find_dotenv())
client: OpenAI = OpenAI()

# Initialize sessions state variables

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# st.title("ChatGPT like Chatbot with Assistants API")

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    # Create a thread and store its id at session_state
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.write("thread id: ", thread.id)

# Main chat interface setup

st.title("OpenAI Assistant API ChatBot Application")
st.write("This is a simple chat application that uses OpenAI's Assistant APIS to generate responses.")

# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
    # Initailize the model and messages list if not already in session state
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo-1106"
    if "messages" not in st.session_state:
        st.session_state.messages:list[dict] = [] 

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for user
    if prompt := st.chat_input("What's up?"):
        # Add user message to state and display it
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user's messages to existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="Please answer the queries using the best of your knowledge."
        )

        # Poll for the run to complete and retrieve the assistant's messages
        while run.status != "completed" :
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        
        # Retrieve messages added by assistant
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]

        for message in assistant_messages_for_run:
            full_response = message.content[0].text.value
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
            with st.chat_message("assistant"):
                st.markdown(full_response)
