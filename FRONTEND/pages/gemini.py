import streamlit as st
import google.generativeai as genai
import time  # For animations

# Configure Gemini API
GENAI_API_KEY = "AIzaSyBmOqZnpAv-X6u33HRUJAPNaFMArT0HmV0"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)

# Load the model
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"Error initializing model: {e}")

# Streamlit App Layout
st.markdown(
    """
    <style>
    body {
        background-color: #FFFAF0;
    }
    .main {
        background-color: #FFFAF0; /* Apply background to Streamlit main area */
    }
    .chat-container {
        background-color: #f0f2f5;
        padding: 15px;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #d1e7ff;
        padding: 8px;
        border-radius: 8px;
        margin: 5px 0;
    }
    .bot-message {
        background-color: #e2f7d4;
        padding: 8px;
        border-radius: 8px;
        margin: 5px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 finance Chatbot🕹")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role, text = msg
    if role == "user":
        st.markdown(f'<div class="user-message">👤 {text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">🤖 {text}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# User input
user_input = st.text_input("Ask something:")

if st.button("Send") and user_input:
    # Add user message to history
    st.session_state.messages.append(("user", user_input))

    try:
        # Get response from Gemini
        with st.spinner("Thinking..."):
            time.sleep(1)  # Fake delay for smooth animation
            response = model.generate_content(user_input)
            bot_response = response.text.strip()

        # Add bot response to history
        st.session_state.messages.append(("bot", bot_response))
        st.rerun()

    except Exception as e:
        st.error(f"API Error: {e}")


