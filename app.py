import uuid

import streamlit as st

from backend.graph import build_graph


st.set_page_config(
    page_title="Weather Advisory Support Bot",
    page_icon="🌦️",
    layout="centered",
)


@st.cache_resource
def get_graph():
    return build_graph()


app = get_graph()


if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("🌦️ Weather Advisory Support Bot")
st.caption("Live weather + traceable SOP-based outdoor safety guidance")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


question = st.chat_input(
    "Ask about outdoor activities, travel, exercise, or weather..."
)


if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    with st.chat_message("assistant"):
        with st.spinner("Checking live weather and applicable SOPs..."):
            try:
                result = app.invoke(
                    {
                        "user_question": question
                    },
                    config=config,
                )

                answer = result["final_answer"]

            except Exception:
                answer = (
                    "I could not complete the weather advisory request. "
                    "Please try again."
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )