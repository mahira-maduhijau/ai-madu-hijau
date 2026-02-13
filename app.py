import streamlit as st
from openai import OpenAI

# --- 1. KONFIGURASI OPENAI ---
# Ganti nama di Secrets Streamlit menjadi: OPENAI_API_KEY
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("API Key OpenAI tidak ditemukan di Secrets!")
    st.stop()

client = OpenAI(api_key=api_key)

# --- 2. KNOWLEDGE BASE MADU HIJAU ---
KNOWLEDGE_BASE = """
Kamu adalah Mahira, Customer Service Madu Hijau yang ramah dan solutif.
Profil: Madu Hijau Original untuk asam lambung, kembung, dan perih.
Harga: 150rb/botol. Promo: 2 botol 250rb.
Aturan: Gunakan panggilan 'Kak'. Jika user komplain berat, katakan akan disambungkan ke Admin.
"""

# --- 3. UI STREAMLIT ---
st.set_page_config(page_title="Mahira - Madu Hijau", page_icon="🍯")
st.title("🍯 Chat dengan Mahira (OpenAI)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Chat
if prompt := st.chat_input("Ada yang bisa Mahira bantu?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Memanggil model GPT-4o-mini (Sangat pintar & paling murah)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": KNOWLEDGE_BASE},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=0.7
            )
            
            res_text = response.choices[0].message.content
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            
        except Exception as e:
            st.error(f"Terjadi kendala: {str(e)}")
