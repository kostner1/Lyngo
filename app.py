import streamlit as st
import openai
import requests
from io import BytesIO

# === Configuration ===
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
ELEVENLABS_VOICE_ID = st.secrets["ELEVENLABS_VOICE_ID"]
openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="Lyngo Agents Demo", layout="centered")
st.title("🧠 Lyngo Agents – Hospitality Booking")
st.write("Talk to your AI receptionist in Egyptian Arabic.")

# === Text Input Instead of Audio ===
st.subheader("📝 Type Your Request")
user_input = st.text_input("Enter your message to the receptionist:")

if user_input:
    st.subheader("🤖 AI Agent Response")
    messages = [
        {
            "role": "system",
            "content": (
                "You're a friendly Egyptian receptionist working at a restaurant. "
                "Reply only in Egyptian Arabic. Keep it short and natural."
            )
        },
        {"role": "user", "content": user_input}
    ]
    with st.spinner("Thinking in Egyptian Arabic..."):
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        agent_reply = gpt_response.choices[0].message.content.strip()
        st.markdown(f"**Agent:** {agent_reply}")

    # === Text to Speech
    st.subheader("🗣️ Spoken Reply")
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": agent_reply,
        "voice_id": ELEVENLABS_VOICE_ID,
        "model_id": "eleven_monolingual_v1",
        "output_format": "mp3"
    }
    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        st.audio(BytesIO(response.content), format='audio/mp3')
    else:
        st.error("Failed to generate voice. Check ElevenLabs setup.")
