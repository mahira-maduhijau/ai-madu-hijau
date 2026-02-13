import streamlit as st
import google.generativeai as genai
import time

# --- 1. KONFIGURASI API & DATA MADU HIJAU ---
# Ganti dengan API Key Gemini kamu
GENAI_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GENAI_API_KEY)

# Data Pengetahuan Produk (Knowledge Base)
KNOWLEDGE_BASE = """
PROFIL PRODUK: Madu Hijau Original.
MANFAAT: Membantu meredakan asam lambung (GERD), perut kembung, perih, dan meningkatkan imun.
KOMPOSISI: Madu Hutan, Ekstrak Daun Kelor, Bidara, Sirih, dan Spirulina.
CARA MINUM: 1 sendok makan, 3x sehari sebelum makan.
HARGA: Rp150.000/botol. Promo: Beli 2 Rp250.000.
LEGALITAS: BPOM RI TR203611111 & Halal MUI.
"""

# --- 2. SETUP MODEL AI ---
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 512,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=f"""
    Nama kamu adalah Sarah, Health Assistant Madu Hijau. 
    Gunakan data berikut sebagai referensi utama: {KNOWLEDGE_BASE}
    
    ATURAN:
    1. Gunakan panggilan 'Kak' agar ramah.
    2. Jika user ingin beli, tanyakan Nama, Alamat, dan Jumlah Pesanan.
    3. Jika user bertanya di luar Madu Hijau atau masalah lambung, katakan kamu tidak tahu.
    4. Jika user marah, komplain, atau minta bicara dengan orang, katakan: [OPER_KE_ADMIN]
    """
)

# --- 3. INTERFACE STREAMLIT ---
st.set_page_config(page_title="CS Madu Hijau AI", page_icon="🍯")
st.title("🍯 CS Madu Hijau - AI Assistant")

# Inisialisasi Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "status" not in st.session_state:
    st.session_state.status = "BOT"  # Status awal adalah BOT

# Tombol Reset untuk Admin (Simulasi)
if st.sidebar.button("Reset Chat"):
    st.session_state.messages = []
    st.session_state.status = "BOT"
    st.rerun()

# Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. LOGIKA PEMROSESAN CHAT ---
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # 1. Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Respon berdasarkan Status
    with st.chat_message("assistant"):
        if st.session_state.status == "HUMAN":
            response = "⏳ *Admin sedang membaca riwayat chat ini dan akan segera membalas langsung...*"
            st.markdown(response)
        else:
            # Panggil AI
            chat = model.start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]
            ])
            
            with st.spinner("Sarah sedang mengetik..."):
                ai_response = chat.send_message(prompt).text
            
            # Cek apakah harus oper ke admin
            if "[OPER_KE_ADMIN]" in ai_response or "admin" in prompt.lower():
                st.session_state.status = "HUMAN"
                response = "Maaf Kak, untuk kendala ini Sarah akan sambungkan langsung ke Konsultan Senior kami ya. Mohon tunggu sebentar, Kakak akan dihubungi kembali via chat ini."
                # Di sini kamu bisa tambahkan fungsi kirim notifikasi ke Telegram/WA Admin
                st.sidebar.warning("⚠️ NOTIFIKASI ADMIN: Pelanggan butuh bantuan manusia!")
            else:
                response = ai_response
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Tampilan Status di Sidebar
st.sidebar.write(f"**Status Saat Ini:** {st.session_state.status}")
if st.session_state.status == "HUMAN":
    st.sidebar.info("💡 Mode Admin Aktif. AI dinonaktifkan.")
