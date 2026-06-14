import streamlit as st
from langgraph_backend import chatbot #importing the backend
from langchain_core.messages import HumanMessage
import uuid

# **************************************** utility functions *************************

# Generate new chat ID
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

# Reset chat
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

#Store thread in sidebar list
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

# Load old conversation from LangGraph
def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

# **************************************** Session Setup ******************************

# this stores the message
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Creates first chat session automatically.
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# Stores list of all chats.
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

# Ensures current chat is added.
add_thread(st.session_state['thread_id'])

# **************************************** Sidebar UI **********************************

# Adding a heading for sidebar 
st.sidebar.title('LangGraph Chatbot')

# Adding a function to the button (this will reset the chat)
if st.sidebar.button('New Chat'): # Starts fresh conversation.
    reset_chat()

# another type of heading 
st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)): # loades the chat history of that conversation (thread)  ** by clicking that button
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        # Convert LangChain messages → UI format (like ai message with another template and human with other )
        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        # UI is updated with old chat.
        st.session_state['message_history'] = temp_messages

# **************************************** Main UI **************************************

# loading the conversation history
for message in st.session_state['message_history']: # Re-renders entire chat history every time page refreshes.
    with st.chat_message(message['role']): # this line and the next line display the user bubble and assitant bubble 
        st.text(message['content'])

# taking the user input 
user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input}) # Save user message locally 
    with st.chat_message('user'): # Show user message immediately
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}   # This tells LangGraph:
                                                                              # “store and continue conversation in this thread”

    # first add the message to message_history
    with st.chat_message('assistant'):
        ai_message = st.write_stream( # Call AI (STREAMING)
            message_chunk.content for message_chunk, metadata in chatbot.stream( # this is the streaming function
                {'messages': [HumanMessage(content=user_input)]},   # send user message to graph
                config=CONFIG,                                      # keep memory using thread_id
                stream_mode='messages'                              # stream response chunks
            )
        )

    #updating the history with ai messages 
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message}) 

#-------------------------------X-----------------------------------------------------------

    # Streaming loop:
    # message_chunk.content for message_chunk, metadata in chatbot.stream(...)

    # Each chunk:

    # is a partial AI response
    # gets displayed instantly

    # So it feels like ChatGPT typing.
