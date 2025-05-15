import streamlit as st
import dialogflow
import uuid
import os

# Override e garantir o caminho correto das credenciais
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__),
    "gen-lang-client-0823044576-cc6cc27081c3.json"
)

# ID do seu projeto no GCP / Dialogflow
PROJECT_ID = "newagent-urrr"

# Função que envia texto ao Dialogflow e devolve a resposta
def detect_intent(text, session_id):
    client = dialogflow.SessionsClient()
    session = client.session_path(PROJECT_ID, session_id)
    query_input = dialogflow.types.QueryInput(
        text=dialogflow.types.TextInput(text=text, language_code="pt-BR")
    )
    response = client.detect_intent(session=session, query_input=query_input)
    return response.query_result.fulfillment_text

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Assistente FIAP")
st.title("Chat FIAP 🤖")

# Armazena histórico na sessão
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.session_id = str(uuid.uuid4())  # identifica conversa

# Renderiza histórico
for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["text"])

# Campo de entrada
user_input = st.chat_input("Digite sua pergunta...")
if user_input:
    st.session_state.history.append({"role": "user", "text": user_input})
    st.chat_message("user").write(user_input)

    # Chama Dialogflow
    answer = detect_intent(user_input, st.session_state.session_id)

    st.session_state.history.append({"role": "assistant", "text": answer})
    st.chat_message("assistant").write(answer)
