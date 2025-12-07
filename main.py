import os
from dotenv import load_dotenv
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="styans chatbuddy",
    page_icon="(@-@)",
    layout="centered"
)
def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
INITIAL_RESPONSE = os.getenv("INITIAL_RESPONSE", "Hi buddy! It's me, styans chatbuddy!")
INITIAL_MSG = os.getenv("INITIAL_MSG", "styans chatbuddy here!")
CHAT_CONTEXT = os.getenv("CHAT_CONTEXT", "You are styans chatbuddy. You speak silly, slow, and funny.")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY не найден в .env!")
else:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq()


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]


st.title("Patrick Chat Buddy!")
st.caption("Talk with styans chatbuddy")


for message in st.session_state.chat_history:
    avatar_icon = "🗨️" if message["role"] == "user" else "🐙"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])


user_prompt = st.chat_input("Ask styans chatbuddy something...")


if user_prompt:

    with st.chat_message("user", avatar="🗨️"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})


    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history
    ]

    
    if GROQ_API_KEY:
        with st.chat_message("assistant", avatar='🐙'):
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # рабочая модель для чата
                messages=messages,
                stream=True
            )
            response = st.write_stream(parse_groq_stream(stream))
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    else:
        warning_msg = "⚠️ Не могу подключиться к Groq без GROQ_API_KEY."
        st.session_state.chat_history.append({"role": "assistant", "content": warning_msg})
        st.warning(warning_msg)
