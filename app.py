import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io
import base64

# --- 1. KONFIGIRASYON PAJ LA ---
st.set_page_config(page_title="Lakay Pale Pro", page_icon="🇭🇹", layout="wide")

# --- 2. STYLE (CSS POU FÈ L BÈL SAN FOTO) ---
st.markdown("""
    <style>
    /* Background Nwa */
    .stApp { background-color: #000000 !important; color: white; }
    
    /* Gwo Tit Neon (Ranplase Logo Lakay Pale a) */
    .neon-text {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(#00d2ff, #ff003c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    /* Tit Segondè */
    .sub-text {
        text-align: center;
        color: #888;
        font-size: 1rem;
        margin-bottom: 30px;
    }

    /* Bwat Sponsor (Ranplase Foto Prestige la) */
    .sponsor-card {
        border: 2px solid #FFD700;
        border-radius: 15px;
        background: #1a1a00;
        text-align: center;
        padding: 20px;
        margin-top: 10px;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
    }

    /* Kache Kamera lè l pa itilize */
    .stExpander {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        border-radius: 10px;
    }
    
    /* Bouton yo */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: #111;
        color: white;
        border: 1px solid #444;
    }
    .stButton>button:hover { border-color: #00d2ff; color: #00d2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (API KEY) ---
with st.sidebar:
    st.markdown("### 🤖 KreyolAIHub")
    st.divider()
    api_key = st.text_input("Kle API OpenAI", type="password")
    if not api_key:
        st.warning("Mete Kle API a la.")
        st.stop()
client = OpenAI(api_key=api_key)

# --- 4. HEADER (TÈKS NEON) ---
st.markdown('<h1 class="neon-text">LAKAY PALE</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Entèlijans Atifisyèl Ayisyen 🇭🇹</p>', unsafe_allow_html=True)

# --- 5. FONKSYON POU KREYE LOGO ---
def generate_logo(prompt):
    with st.spinner("🎨 M ap desinen logo a... Tann 10 segonn."):
        try:
            response = client.images.generate(
                model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1
            )
            return response.data[0].url
        except Exception as e:
            return f"Erè: {str(e)}"

# --- 6. LAYOUT (3 KOLÒN) ---
c_sponsor, c_voice, c_scan = st.columns([1, 2, 2])

# --- KOLÒN 1: SPONSOR (CSS) ---
with c_sponsor:
    st.markdown("""
        <div class="sponsor-card">
            <h3 style="color:#FFD700; margin:0;">SPONSOR</h3>
            <div style="font-size: 40px;">🍺</div>
            <p style="color:white; font-weight:bold;">PRESTIGE</p>
            <p style="color:#aaa; font-size:12px;">Byè Peyi a</p>
        </div>
    """, unsafe_allow_html=True)

# --- KOLÒN 2: PALE & KREYE ---
with c_voice:
    st.info("🎙️ **PALE / KREYE**")
    st.write("Di: *'Fè yon logo pou...'*")
    
    # Mikwo
    audio_data = mic_recorder(start_prompt="🔴 PALE", stop_prompt="⬛ STOP", key="recorder")
    
    if audio_data:
        # Transkripsyon
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "audio.wav"
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        text = transcript.text
        st.success(f"🗣️ **Ou di:** {text}")

        # Lojik: Si w mande desen, li desinen. Sinon li pale.
        mots_cles = ["logo", "imaj", "desen", "foto", "image", "design", "fè"]
        if any(w in text.lower() for w in mots_cles):
            st.warning("🎨 M ap travay sou desen an...")
            url = generate_logo(text)
            if "http" in url: st.image(url)
            else: st.error(url)
        else:
            resp = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":text}])
            st.write(f"🤖 {resp.choices[0].message.content}")

# --- KOLÒN 3: ESKANÈ (KACHE) ---
with c_scan:
    st.error("📸 **ESKANÈ**")
    
    # Kamera kache nan yon tiwa
    with st.expander("📸 Klike pou wouvri Kamera a"):
        cam = st.camera_input("Pran foto a")
    
    up = st.file_uploader("Oswa upload yon foto", type=['jpg','png'])
    final = cam if cam else up

    if final:
        st.image(final, width=150)
        if st.button("🔍 ANALIZE"):
            with st.spinner("M ap gade..."):
                b64 = base64.b64encode(final.getvalue()).decode()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":[{"type":"text", "text":"Esplike sa."},{"type":"image_url", "image_url":{"url":f"data:image/jpeg;base64,{b64}"}}] }])
                st.write(res.choices[0].message.content)
