import streamlit as st
import google.generativeai as genai
import os
import time
from PIL import Image
import PyPDF2

st.set_page_config(page_title="ScopeAI Pro v2", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .stChatMessage {padding: 1rem; border-radius: 10px; margin-bottom: 1rem}
    [data-testid="stChatMessageContent"] p {font-size: 16px}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro')

SYSTEM_PROMPT = """Tu ScopeAI Pro hai. NCERT ka sabse smart teacher.
Class 6-12 ke students ko Hinglish mein padhata hai. 
Step-by-step samjha, examples de, "Shabash beta" bol ke motivate kar.
Math ke formula LaTeX mein de: $x^2 + y^2 = z^2$"""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Shabash beta! ScopeAI Pro v2 mein swagat hai 🚀 Kya padhna hai aaj?"})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def stream_response(prompt):
    response = model.generate_content(prompt, stream=True)
    full_text = ""
    placeholder = st.empty()
    for chunk in response:
        if chunk.text:
            full_text += chunk.text
            placeholder.markdown(full_text + "▌")
            time.sleep(0.02)
    placeholder.markdown(full_text)
    return full_text

prompt = st.chat_input("Sawal pucho ya file bhejo...")
uploaded_file = st.file_uploader("PDF/Image", type=['pdf','png','jpg','jpeg'], label_visibility="collapsed")

if prompt or uploaded_file:
    user_content = prompt if prompt else "File ka analysis karo"
    if uploaded_file:
        st.session_state.messages.append({"role": "user", "content": f"📎 {uploaded_file.name}"})
        with st.chat_message("user"):
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, width=300)
            else:
                st.markdown(f"📄 {uploaded_file.name}")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    pdf_text = "".join([page.extract_text() for page in pdf_reader.pages])
                    final_prompt = f"{SYSTEM_PROMPT}\n\nPDF Content:\n{pdf_text}\n\nUser: {user_content}"
                    reply = stream_response(final_prompt)
                else:
                    img = Image.open(uploaded_file)
                    final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_content}"
                    reply = stream_response([final_prompt, img])
            else:
                final_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}"
                reply = stream_response(final_prompt)
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Bhai error: {e}")
