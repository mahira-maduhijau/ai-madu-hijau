import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURASI API ---
# Pastikan di Secrets kamu menulis: GENAI_API_KEY = "AIza..."
api_key = st.secrets.get("GENAI_API_KEY")

if not api_key:
    st.error("API Key tidak ditemukan! Masuk ke Settings > Secrets di Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# --- 2. DATA PRODUK ---
KNOWLEDGE_BASE = "Kamu adalah Mahira, asisten ramah Madu Hijau. Produk ini untuk asam lambung, harga 150rb. Jika bingung atau user marah, minta maaf dan katakan akan panggil Admin."

# --- 3. INISIALISASI MODEL ---
# Kita langsung pakai 'gemini-1.5-flash' karena ini yang paling umum sekarang
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# --- 4. UI CHAT ---
st.title("🍯 Asisten Mahira")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya Mahira di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Gabungkan instruksi Mahira dengan pertanyaan user
            full_prompt = f"Instruksi: {KNOWLEDGE_BASE}\n\nUser: {prompt}"
            response = model.generate_content(full_prompt)
            res_text = response.text
            
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
        except Exception as e:
            st.error(f"Aduh, ada masalah teknis: {str(e)}")
            st.info("Saran: Coba buat API Key baru di Google AI Studio dan ganti yang lama di Secrets.")
