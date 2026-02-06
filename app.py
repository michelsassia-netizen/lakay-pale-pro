import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io
import base64

# --- 1. CONFIG & STYLE (MINIMALIST NWA) ---
st.set_page_config(page_title="Lakay Pale", page_icon="🇭🇹", layout="wide")

st.markdown("""
    <style>
    /* Background Nwa Total */
    .stApp { background-color: #000000 !important; color: white; }
    
    /* Tit Senp & Pwòp */
    h1 { 
        text-align: center; 
        font-family: sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#eee, #999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 40px;
    }
    
    /* Bwat Sponsor (Gòch) */
    .sponsor-box {
        border: 1px solid #FFD700; /* Gold */
        background: #111;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        height: 400px; /* Wotè fiks pou l parèt byen */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* Seksyon Mitan & Dwat */
    .action-box {
        background: #111;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        height: 100%;
    }

    /* Bouton */
    .stButton>button { 
        width: 100%; 
        border-radius: 30px; 
        background: #222; 
        color: white; 
        border: 1px solid #444;
        padding: 10px;
    }
    .stButton>button:hover { border-color: #00d2ff; color: #00d2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTÈM (API KEY) ---
with st.sidebar:
    st.header("⚙️ Kle a")
    api_key = st.text_input("API Key", type="password", label_visibility="collapsed")
    if not api_key:
        st.warning("Mete Kle a la.")
        st.stop()

client = OpenAI(api_key=api_key)

# --- 3. FONKSYON POU FÒSE KREYÒL ---
def ask_ai_creole(user_input, context="general"):
    # Lòd strik pou AI la pale Kreyòl sèlman
    system_prompt = "Ou se 'Lakay Pale'. Ou pale KREYÒL AYISYEN SÈLMAN. Kèlkeswa lang moun nan pale (Anglè, Fransè, Panyòl), ou reponn an KREYÒL. Si yo mande w kreye yon bagay, esplike sa w fè a an Kreyòl."
    
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
    
    with st.spinner("⏳..."):
        res = client.chat.completions.create(model="gpt-4o", messages=messages)
        return res.choices[0].message.content

def create_image(prompt):
    with st.spinner("🎨 M ap kreye l..."):
        try:
            # Nou amelyore prompt la pou rezilta a bèl
            final_prompt = f"High quality, artistic representation of: {prompt}"
            res = client.images.generate(model="dall-e-3", prompt=final_prompt, size="1024x1024", quality="standard", n=1)
            return res.data[0].url
        except:
            return None

# --- 4. LAYOUT MINIMALIST (3 KOLÒN) ---
st.title("LAKAY PALE")

# Nou bay Mitan ak Dwat plis espas (1, 2, 2)
col_sponsor, col_voice, col_scan = st.columns([1, 2, 2])

# === KOLÒN 1: SPONSOR ===
with col_sponsor:
    st.markdown("""
        <div class="sponsor-box">
            <h3 style="color: #FFD700;">SPONSOR</h3>
            <div style="font-size: 40px;">🍺</div>
            <p style="color: #888;">Espace Réservé</p>
        </div>
    """, unsafe_allow_html=True)

# === KOLÒN 2: MIKWO & KREYASYON ===
with col_voice:
    st.markdown("<div class='action-box'>", unsafe_allow_html=True)
    st.info("🎙️ **MANDE / KREYE (Tout bagay)**")
    st.write("Di sa w vle a. Si w vle yon imaj, di 'Fè yon...'")
    
    audio = mic_recorder(start_prompt="🔴 PALE", stop_prompt="⬛ STOP", key="recorder")
    
    if audio:
        # Transkripsyon
        buff = io.BytesIO(audio['bytes'])
        buff.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=buff)
        text = trans.text
        st.write(f"🗣️: {text}")

        # Lojik: Èske li vle yon Imaj oswa Tèks?
        keywords_img = ["kreye", "fè yon imaj", "fè yon logo", "desinen", "create", "draw"]
        if any(w in text.lower() for w in keywords_img):
            # Kreye Imaj
            st.success("🎨 OK, m ap desinen sa pou ou.")
            url = create_image(text)
            if url: st.image(url)
        else:
            # Repons Tèks (Kreyòl Sèlman)
            repons = ask_ai_creole(text)
            st.markdown(f"**🤖 Repons:** {repons}")
    st.markdown("</div>", unsafe_allow_html=True)

# === KOLÒN 3: DOKIMAN & ESKANÈ ===
with col_scan:
    st.markdown("<div class='action-box'>", unsafe_allow_html=True)
    st.error("📸 **ESKANE DOKIMAN**")
    st.write("M ap esplike w nenpòt papye an Kreyòl.")
    
    # Kamera
    cam = st.camera_input("Pran foto a")
    up = st.file_uploader("Oswa upload yon fichye", type=['jpg','png'])
    
    final_file = cam if cam else up

    if final_file:
        st.image(final_file, width=200)
        if st.button("🔍 ESPLIKE M SA AN KREYÒL"):
            b64 = base64.b64encode(final_file.getvalue()).decode()
            
            # Prompt espesyal pou tradiksyon dokiman
            prompt_doc = "Gade imaj sa a. Se yon dokiman (Lèt, Fakt, Medikal, elatriye). Esplike m an DETAY kisa li di, men reponn mwen an KREYÒL AYISYEN SÈLMAN. Pa pale lòt lang."
            
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user", "content":[{"type":"text","text":prompt_doc},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}]
            )
            st.info(f"📄 **Men sa papye a di:**\n\n{res.choices[0].message.content}")
    st.markdown("</div>", unsafe_allow_html=True)
