import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io
import os
import base64

# --- CONFIG ---
st.set_page_config(page_title="Lakay Pale Pro", page_icon="🇭🇹", layout="wide")

# --- STYLE (Kamera Kache + Neon) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    
    /* Header Style */
    h1 { 
        text-align: center; 
        background: -webkit-linear-gradient(#00d2ff, #ff003c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent; 
        font-weight: 800;
        font-size: 3rem;
    }
    
    /* Bwat Sponsor */
    .sponsor-box {
        border: 2px dashed #FFD700;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        background: #111;
        color: #FFD700;
        margin-bottom: 20px;
    }

    /* Kache Kamera a nan yon Tiwa */
    .stExpander {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ SISTÈM")
    api_key = st.text_input("Kle API OpenAI", type="password")
    if not api_key:
        st.warning("Mete Kle a pou kòmanse.")
        st.stop()
client = OpenAI(api_key=api_key)

# --- HEADER (LOGOS) ---
c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    if os.path.exists("kreyolaihub.png"): st.image("kreyolaihub.png", width=120)
    else: st.info("Manque: kreyolaihub.png")
with c2:
    st.markdown("<h1>LAKAY PALE</h1>", unsafe_allow_html=True)
with c3:
    if os.path.exists("logo.png"): st.image("logo.png", width=120)
    else: st.info("Manque: logo.png")

st.divider()

# --- FONKSYON DESEN (DALL-E 3) ---
def generate_image(prompt):
    with st.spinner("🎨 M ap kreye logo a... Tann 10 segonn."):
        try:
            response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
            return response.data[0].url
        except Exception as e:
            return f"Erè: {str(e)}"

# --- MAIN PAGE (3 KOLÒN) ---
col_spon, col_pale, col_scan = st.columns([1, 2, 2])

# 1. SPONSOR
with col_spon:
    st.markdown('<div class="sponsor-box">ESPACE SPONSOR</div>', unsafe_allow_html=True)

# 2. PALE / KREYE
with col_pale:
    st.info("🎙️ PALE (Di: 'Fè yon logo...')")
    audio_data = mic_recorder(start_prompt="🔴 PALE", stop_prompt="⬛ STOP", key="recorder")
    
    if audio_data:
        # Transkripsyon
        audio_file = io.BytesIO(audio_data['bytes'])
        audio_file.name = "audio.wav"
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        text = transcript.text
        st.write(f"🗣️ **Ou di:** {text}")

        # DETEKSYON POU FÈ DESEN
        mots_cles = ["logo", "imaj", "desen", "foto", "image", "créez", "create", "fè"]
        if any(w in text.lower() for w in mots_cles) and ("logo" in text.lower() or "imaj" in text.lower()):
            st.success("🎨 OK! M ap desinen sa pou ou kounye a!")
            img_url = generate_image(text)
            if "http" in img_url: st.image(img_url)
            else: st.error(img_url)
        else:
            # Pale Nòmal
            resp = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":text}])
            st.write(resp.choices[0].message.content)

# 3. ESKANÈ (KACHE)
with col_scan:
    st.error("📸 ESKANÈ")
    
    # MEN REZILTA A: Kamera a kache isit la!
    with st.expander("📸 Klike la pou wouvri Kamera a"):
        cam = st.camera_input("Pran foto a")
    
    up = st.file_uploader("Oswa upload yon fichye", type=['jpg','png'])
    final = cam if cam else up

    if final:
        st.image(final, width=200)
        if st.button("🔍 ANALIZE"):
            with st.spinner("M ap gade..."):
                b64 = base64.b64encode(final.getvalue()).decode()
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":[{"type":"text", "text":"Esplike sa."},{"type":"image_url", "image_url":{"url":f"data:image/jpeg;base64,{b64}"}}] }])
                st.write(res.choices[0].message.content)
