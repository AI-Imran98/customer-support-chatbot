import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found! Please add it to your .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="AI Customer Support", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .main-header { background: linear-gradient(135deg, #534AB7 0%, #0F6E56 100%); padding: 1.2rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; }
    .main-header h1 { font-size: 1.6rem; margin: 0; font-weight: 600; }
    .main-header p { margin: 4px 0 0 0; opacity: 0.85; font-size: 0.9rem; }
    .status-dot { display: inline-block; width: 8px; height: 8px; background: #28a745; border-radius: 50%; margin-right: 6px; }
    .stat-badge { display: inline-block; background: #EEEDFE; color: #3C3489; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 500; margin: 3px 2px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Bot Configuration")
    st.markdown("---")
    business_name = st.text_input("Business Name", value="Tech Solution BD")
    business_type = st.selectbox("Business Type", ["E-commerce / Online Shop","Software / IT Company","Restaurant / Food Delivery","Healthcare / Clinic","Education / Coaching","Real Estate","General Business"])
    tone = st.select_slider("Conversation Tone", options=["Very Formal","Formal","Friendly","Very Friendly"], value="Friendly")
    temperature = st.slider("AI Creativity", 0.0, 1.0, 0.7, 0.1)
    st.markdown("---")
    msg_count = len(st.session_state.get("messages", []))
    st.markdown("### 📊 Chat Stats")
    st.markdown(f'<span class="stat-badge">💬 Messages: {msg_count}</span> <span class="stat-badge">🤖 Gemini Flash</span>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

def build_system_prompt(business_name, business_type, tone):
    tone_map = {"Very Formal": "Use very polite and professional language.", "Formal": "Use professional but simple language.", "Friendly": "Be warm, approachable, and easy to talk to.", "Very Friendly": "Be casual and fun, use emojis where appropriate."}
    return f"""You are an expert customer support assistant for {business_name}. Business type: {business_type}. Always respond in English only. Tone: {tone_map[tone]}. Never give false information. If you don't know, say so honestly."""

def get_chat_session(system_prompt, temperature):
    if "chat_session" not in st.session_state or st.session_state.chat_session is None:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_prompt, generation_config=genai.GenerationConfig(temperature=temperature, max_output_tokens=1024))
        st.session_state.chat_session = model.start_chat(history=[])
    return st.session_state.chat_session

st.markdown(f'<div class="main-header"><h1>🤖 {business_name} — AI Support</h1><p><span class="status-dot"></span>Online | {business_type} | English Support</p></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(f"Hello! 👋 I'm {business_name}'s AI assistant. How can I help you today?")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                chat = get_chat_session(build_system_prompt(business_name, business_type, tone), temperature)
                response = chat.send_message(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

st.markdown("---")
st.markdown("**⚡ Quick Questions:**")
col1, col2, col3, col4 = st.columns(4)
for col, question in {col1: "What services do you offer?", col2: "How can I contact you?", col3: "I want to track my order", col4: "What is your refund policy?"}.items():
    with col:
        if st.button(question, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            chat = get_chat_session(build_system_prompt(business_name, business_type, tone), temperature)
            response = chat.send_message(question)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
