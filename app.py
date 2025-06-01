
import streamlit as st
import openai
import requests
import tempfile
from io import BytesIO

# === Configuration ===
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
ELEVENLABS_VOICE_ID = st.secrets["ELEVENLABS_VOICE_ID"]
openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="Lyngo Agents Demo", layout="centered")
st.title("🧠 Lyngo Agents – Hospitality Booking")
st.write("Talk to your AI receptionist in Egyptian Arabic.")

# === Record Audio ===
with st.expander("🎙️ Start Talking"):
    audio_file = st.audio_recorder("Record a message", format="audio/wav")

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_file.read())
        audio_path = temp_audio.name

    # === Step 1: Transcribe ===
    st.subheader("🔍 Transcription")
    with st.spinner("Transcribing your voice..."):
        audio_file.seek(0)
        transcript = openai.Audio.transcribe("whisper-1", file=open(audio_path, "rb"))
        st.write("You said:", transcript["text"])

    # === Step 2: Get Response (GPT-4o) ===
    st.subheader("🤖 AI Agent Response")
    messages = [
        {"role": "system", "content": "You're a friendly Egyptian receptionist working at a restaurant. Reply only in Egyptian Arabic. Keep it short and natural."},
        {"role": "user", "content": transcript["text"]}
    ]
    with st.spinner("Thinking in Egyptian Arabic..."):
        gpt_response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
        agent_reply = gpt_response.choices[0].message.content.strip()
        st.markdown(f"**Agent:** {agent_reply}")

    # === Step 3: Text to Speech (ElevenLabs) ===
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
    response = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                             headers=headers, json=payload)
    if response.status_code == 200:
        st.audio(BytesIO(response.content), format='audio/mp3')
    else:
        st.error("Failed to generate voice. Check ElevenLabs setup.")

    # === Step 4: Booking Confirmation Storage (Mock)
    if "book" in transcript["text"].lower():
        name = "Guest"
        time = "8 PM"
        st.success(f"✅ Booking stored: Table for 2 at {time} under the name {name}.")

    # === Bonus: Language Toggle
    if st.checkbox("🧪 Try in MSA or English (basic plan simulation)"):
        alt_msg = [
            {"role": "system", "content": "You're a receptionist replying in neutral Modern Standard Arabic."},
            {"role": "user", "content": transcript["text"]}
        ]
        alt_response = openai.ChatCompletion.create(model="gpt-4o", messages=alt_msg)
        alt_reply = alt_response.choices[0].message.content.strip()
        st.info(f"**MSA Reply:** {alt_reply}")
        payload["text"] = alt_reply
        alt_voice = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                                  headers=headers, json=payload)
        if alt_voice.status_code == 200:
            st.audio(BytesIO(alt_voice.content), format='audio/mp3')
