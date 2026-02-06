import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io
import base64
import urllib.parse

# --- 1. SETTINGS & CYBER-LUXURY DESIGN ---
st.set_page_config(page_title="Lakay Pale Pro", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    /* Obsidian Black Base */
    .stApp { background-color: #050505 !important; color: #ffffff !important; }
    
    /* Neon Glassmorphism Cards */
    div[data-testid="stVerticalBlock"] > div:has(div.blue-card) {
        border: 2px solid #00d2ff !important;
        border-radius: 25px !important;
        padding: 30px !important;
        background: rgba(0, 210, 255, 0.05) !important;
        box-shadow: 0px 0px 30px rgba(0, 210, 255, 0.4) !important;
    }

    div[data-testid="stVerticalBlock"] > div:has(div.red-card) {
        border: 2px solid #ff003c !important;
        border-radius: 25px !important;
        padding: 30px !important;
        background: rgba(255, 0, 60, 0.05) !important;
        box-shadow: 0px 0px 30px rgba(255, 0, 60, 0.4) !important;
    }

    /* Glow Title */
    .glow-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(40px, 8vw, 70px);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #ff003c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 20px rgba(255, 255, 255, 0.1);
    }

    /* Haptic Feedback (Vibration) Simulation */
    @keyframes vibrate {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
    .vibrate-effect { animation: vibrate 0.3s linear 2; }
    </style>
    
    <script>
    function triggerVibrate() {
        if (window.navigator && window.navigator.vibrate) {
            window.navigator.vibrate([100, 50, 100]);
        }
    }
    </script>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & SESSION STATE ---
if 'msg_count' not in st.session_state: st.session_state.msg_count = 0
if 'total_cost' not in st.session_state: st.session_state.total_cost = 0.0
if 'total_calls' not in st.session_state: st.session_state.total_calls = 0

# --- 3. SIDEBAR (Admin & System) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00d2ff;'>⚙️ SISTÈM</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Kle API OpenAI:", type="password")
    profile = st.selectbox("Chwazi Profile:", ["Jeneral", "Lekòl", "Lopital", "Restoran"])
    
    st.markdown("---")
    admin_pass = st.text_input("Admin Dashboard:", type="password")
    if admin_pass == "LakayPro2026":
        st.markdown("<h3 style='color:#00ff88;'>📊 ADMIN DASHBOARD</h3>", unsafe_allow_html=True)
        st.metric("Total Mesaj", st.session_state.total_calls)
        st.metric("Depans Estime ($)", f"{st.session_state.total_cost:.4f}")

# --- 4. MAIN UI ---
st.markdown('<h1 class="glow-title">LAKAY PALE</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888;">Entèlijans ki Pale Lang Ou (Kreyòl)</p>', unsafe_allow_html=True)

# 5-Message Limit Progress Bar
remaining = 5 - st.session_state.msg_count
if remaining > 0:
    st.progress(st.session_state.msg_count / 5)
    st.markdown(f"<p style='text-align:center; color:#00d2ff;'>{st.session_state.msg_count}/5 Mesaj Itilize</p>", unsafe_allow_html=True)
else:
    st.error("❌ Limit Rive! Kontakte nou pou vèsyon Pro pou w kontinye.")

if api_key:
    client = OpenAI(api_key=api_key)
    col1, col2 = st.columns(2, gap="large")

    # --- COLUMN 1: VOICE/STUDIO ---
    with col1:
        st.markdown('<div class="blue-card"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown("<h2 style='color:#00d2ff; text-align:center;'>🎙️ Pale / Kreye</h2>", unsafe_allow_html=True)
            if remaining > 0:
                audio = mic_recorder(start_prompt="🎤 KÒMANSE PALE", stop_prompt="🛑 FINI", key='mic')
                if audio:
                    with st.spinner("AI ap reflechi..."):
                        # Whisper Transcription
                        audio_bio = io.BytesIO(audio['bytes']); audio_bio.name = "audio.wav"
                        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_bio)
                        
                        # AI Response (gpt-4o-mini for cost saving)
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": f"Ou se yon asistan {profile}. Reponn sèlman an kreyòl ayisyen."},
                                      {"role": "user", "content": transcript.text}]
                        )
                        st.session_state.msg_count += 1
                        st.session_state.total_calls += 1
                        st.session_state.total_cost += 0.002
                        st.write(f"**Ou di:** {transcript.text}")
                        st.success(res.choices[0].message.content)
                        st.markdown('<script>triggerVibrate();</script>', unsafe_allow_html=True)

    # --- COLUMN 2: SCANNER ---
    with col2:
        st.markdown('<div class="red-card"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown("<h2 style='color:#ff003c; text-align:center;'>📄 Eskanè</h2>", unsafe_allow_html=True)
            if remaining > 0:
                img_file = st.file_uploader("Voye Foto", type=["jpg", "png"], label_visibility="collapsed")
                if img_file and st.button("✨ ANALIZE DOKIMAN", use_container_width=True):
                    with st.spinner("M ap li papye a..."):
                        img_b64 = base64.b64encode(img_file.getvalue()).decode()
                        # Vision Analysis (gpt-4o)
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": [
                                {"type": "text", "text": f"Esplike dokiman sa a an kreyòl pou profile {profile}."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]}]
                        )
                        st.session_state.msg_count += 1
                        st.session_state.total_calls += 1
                        st.session_state.total_cost += 0.01
                        st.info(res.choices[0].message.content)
                        st.markdown('<script>triggerVibrate();</script>', unsafe_allow_html=True)

else:
    st.warning("👈 Mete Kle API ou a nan sidebar la pou aktive sistèm nan.")

st.markdown("<br><p style='text-align:center; color:#444;'>KreyolAIHub © 2026 | Language Justice for Haiti</p>", unsafe_allow_html=True)