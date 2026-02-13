import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURASI API (AMANKAN DENGAN SECRETS) ---
try:
    # Mengambil API Key dari Advanced Settings > Secrets di Streamlit Cloud
    GENAI_API_KEY = st.secrets["GENAI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
except:
    st.error("Waduh, API Key belum terpasang di Secrets! Silakan cek menu Advanced Settings.")
    st.stop()

# --- 2. DATA MADU HIJAU (KNOWLEDGE BASE) ---
KNOWLEDGE_BASE = """
PROFIL PRODUK: Madu Hijau Original.
MANFAAT: Membantu meredakan asam lambung (GERD), kembung, perih, dan meningkatkan imun.
KOMPOSISI: Madu Hutan, Ekstrak Daun Kelor, Bidara, Sirih, dan Spirulina.
CARA MINUM: 1 sendok makan, 3x sehari sebelum makan.
HARGA: Rp150.000/botol. Promo: Beli 2 Rp250.000.
LEGALITAS: BPOM RI TR203611111 & Halal MUI.
"""

# --- 3. LOGIKA AI ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=f"Kamu adalah Sarah, CS Madu Hijau yang ramah. Gunakan data ini: {KNOWLEDGE_BASE}. Jika ada keluhan berat atau user minta bicara ke orang, katakan kamu akan sambungkan ke Admin (tulis teks: [OPER_KE_ADMIN])."
)

# --- 4. TAMPILAN APLIKASI ---
st.set_page_config(page_title="CS Madu Hijau AI", page_icon="🍯")
st.title("🍯 Asisten Madu Hijau")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "status" not in st.session_state:
    st.session_state.status = "BOT"

# Tampilkan chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Chat
if prompt := st.chat_input("Ada yang bisa Sarah bantu?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.status == "HUMAN":
            res = "⏳ *Admin sedang memproses chat Anda...*"
        else:
            chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]])
            res = chat.send_message(prompt).text
            
            if "[OPER_KE_ADMIN]" in res or "admin" in prompt.lower():
                st.session_state.status = "HUMAN"
                res = "Maaf Kak, Sarah sambungkan ke Admin Konsultan ya. Mohon tunggu sebentar."
                st.sidebar.error("⚠️ NOTIFIKASI: Admin dibutuhkan!")
        
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

st.sidebar.write(f"Status: **{st.session_state.status}**")
