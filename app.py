"""
Interface Streamlit pour le Portfolio Agent
"""
import streamlit as st
import os
from dotenv import load_dotenv
from upstash_vector import Index
from agents import Agent, Runner, ModelSettings, function_tool

load_dotenv(override=True)

st.set_page_config(
    page_title="Yannis MOCUHARD - Assistant IA",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Yannis MOCUHARD - Assistant IA")
st.markdown("Posez vos questions sur mon parcours, mes expériences, mes projets et mes compétences!")

vector_index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

@function_tool
def search_infos(query: str, top_k: int = 5) -> str:
    """Recherche des informations dans les données """
    try:
        results = vector_index.query(
            data=query,
            top_k=top_k,
            include_metadata=True,
            include_data=True
        )
        
        if not results:
            return "Aucun résultat trouvé."
        
        formatted = []
        for i, result in enumerate(results, 1):
            source = result.metadata.get("source", "Unknown")
            data = result.data
            formatted.append(f"[{i}] {source}:\n{data}")
        
        return "\n\n".join(formatted)
    
    except Exception as e:
        return f"Erreur: {str(e)}"

agent = Agent(
    name="agent",
    instructions=""" Tu es Yannis MOCUHARD qui doit répondre au questions des utilisateurs (potentiellement des recruteurs) sur le parcours, les expériences, les projets et les compétences. Utilise les outils à ta disposition pour trouver les informations nécessaires et fournir des réponses précises, pertinentes et professionnelles.
""",
    model="gpt-4.1-nano",
    model_settings=ModelSettings(temperature=0.7),
    tools=[search_infos]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Posez votre question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner(" Recherche en cours..."):
            try:
                result = Runner.run_sync(agent, user_input)
                response = result.final_output
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f" Erreur: {str(e)}"
                st.error(error_msg)
