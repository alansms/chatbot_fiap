import os
import uuid
import streamlit as st
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
from datetime import datetime
import time


# Automatically pick up a Dialogflow service account JSON in the working folder
KEY_FILE = next((f for f in os.listdir() if f.endswith('.json')), None)
if not KEY_FILE:
    raise FileNotFoundError("No service account JSON file found in the working directory.")

# Force the Dialogflow project ID where your agent is deployed
PROJECT_ID = "newagent-urrr"
LANGUAGE_CODE = "pt-BR"

def detect_intent_text(text: str, session_id: str) -> tuple[str, str]:
    # Uses service account JSON for authentication
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        session=session, query_input=query_input
    )
    intent = response.query_result.intent.display_name
    return response.query_result.fulfillment_text, intent

# === Streamlit UI ===

st.set_page_config(page_title="Chat FIAP 🤖", page_icon="🤖")

# Sidebar with logo, quick-reply buttons, and input
 # Sidebar container
with st.sidebar:
    # Display responsive FIAP logo
    st.image("logo_fiap.jpg", use_container_width=True)

    # Clickable quick-reply buttons
    selected = None
    st.markdown("### Menu")
    if st.button("Quais cursos?"):
        selected = "Quais cursos vocês possuem?"
    if st.button("Horário de aula"):
        selected = "Qual é o horário das aulas?"
    if st.button("Contato"):
        selected = "Como faço contato?"
    # Text input and send button
    prompt_input = st.text_input("Digite sua pergunta...", key="sidebar_input")
    if st.button("Enviar"):
        if prompt_input:
            st.session_state.pending = prompt_input

st.title("Chat FIAP 🤖")

if "greet_shown" not in st.session_state:
    hour = datetime.now().hour
    if hour < 12:
        greet = "Bom dia"
    elif hour < 18:
        greet = "Boa tarde"
    else:
        greet = "Boa noite"
    st.write(f"{greet}, Senhor(a)! Eu sou o Chat FIAP 🤖. Como posso ajudar?")
    st.session_state.greet_shown = True

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

for role, msg in st.session_state.history:
    st.chat_message(role).write(msg)

 # Determine the prompt from buttons or sidebar input
prompt = st.session_state.pop("pending", None) or selected

if prompt:
    st.session_state.history.append(("user", prompt))
    st.chat_message("user").write(prompt)

    # simulate typing
    with st.spinner("Digitando..."):
        time.sleep(0.8)
        answer, intent = detect_intent_text(prompt, st.session_state.session_id)

    # Fallback
    if not answer:
        fallback = "Desculpe, não entendi. Pode reformular?"
        st.session_state.history.append(("assistant", fallback))
        st.chat_message("assistant").write(fallback)
    else:
        # show intent name (for debugging)
        st.write(f"*Intent detectada*: {intent}")
        st.session_state.history.append(("assistant", answer))
        st.chat_message("assistant").write(answer)