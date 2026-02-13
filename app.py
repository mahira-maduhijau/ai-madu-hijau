import streamlit as st
import google.generativeai as genai

# --- 1. KONFIGURASI API ---
api_key = st.secrets.get("GENAI_API_KEY")

if not api_key:
    st.error("API Key tidak ditemukan di Secrets!")
    st.stop()

genai.configure(api_key=api_key)

# --- 2. DATA PRODUK ---
KNOWLEDGE_BASE = "Kamu adalah Mahira, asisten ramah Madu Hijau. Produk ini untuk asam lambung, harga 150rb. Jika bingung atau user marah, minta maaf dan katakan akan panggil Admin."

# --- 3. LOGIKA PENCARIAN MODEL YANG AKTIF ---
@st.cache_resource
def get_working_model():
    try:
        # Mencari model yang mendukung 'generateContent' di akunmu
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Mengutamakan flash, tapi jika tidak ada ambil apa saja yang tersedia
                if 'gemini-1.5-flash' in m.name or 'gemini-pro' in m.name:
                    return genai.GenerativeModel(m.name)
        # Jika tidak ketemu di list, paksa pakai gemini-1.5-flash tanpa prefix
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return None

model = get_working_model()

# --- 4. UI CHAT ---
st.set_page_config(page_title="Asisten Mahira", page_icon="🍯")
st.title("🍯 Chat dengan Mahira")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya Mahira..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model is None:
            st.error("Gagal mendapatkan akses ke model Gemini. Cek apakah API Key Anda aktif.")
        else:
            try:
                # Menambahkan konteks agar Mahira tahu identitasnya
                full_query = f"{KNOWLEDGE_BASE}\n\nPertanyaan User: {prompt}"
                response = model.generate_content(full_query)
                res_text = response.text
                
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
            except Exception as e:
                st.error(f"Koneksi terputus: {str(e)}")
