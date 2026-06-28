import streamlit as st
from PIL import Image, JpegImagePlugin, PdfImagePlugin
import re
import io

# Səhifə nizamlamaları
st.set_page_config(page_title="Şəkil -> PDF Çevirici", page_icon="🖼️", layout="centered")

def get_digit_from_name(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0

def add_padding_to_image(img, padding_size=40):
    width, height = img.size
    new_width = width + (padding_size * 2)
    new_height = height + (padding_size * 2)
    padded_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    padded_img.paste(img, (padding_size, padding_size))
    return padded_img

# Veb İnterfeys Dizaynı
st.title("🖼️ Şəkilləri PDF-ə Çevir")
st.write("Şəkilləri yükləyin (adındakı rəqəmlərə görə sıralanacaq) və kənar boşluqlu PDF əldə edin.")

# Ayarlar (Sidebar)
st.sidebar.header("⚙️ Ayarlar")
padding_input = st.sidebar.slider("Kənar boşluq (Padding) ölçüsü:", min_value=0, max_value=100, value=40, step=5)

# Fayl yükləmə komponenti
uploaded_files = st.file_uploader(
    "Şəkilləri seçin və ya bura sürükləyin", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} şəkil seçildi.")
    
    # Şəkilləri istifadəçinin yüklədiyi fayl adına görə (rəqəmsal) sıralayırıq
    sorted_files = sorted(uploaded_files, key=lambda x: get_digit_from_name(x.name))
    
    if st.button("🚀 PDF Hazırla"):
        with st.spinner("Şəkillər emal olunur, xahiş edirik gözləyin..."):
            try:
                # İlk şəkli hazırlayırıq
                first_img = Image.open(sorted_files[0]).convert('RGB')
                first_img_padded = add_padding_to_image(first_img, padding_input)
                
                # Digər şəkilləri hazırlayırıq
                image_list = []
                for file in sorted_files[1:]:
                    img = Image.open(file).convert('RGB')
                    img_padded = add_padding_to_image(img, padding_input)
                    image_list.append(img_padded)
                
                # PDF-i yaddaşda (RAM-da) saxlamaq üçün BytesIO obyektindən istifadə edirik
                pdf_buffer = io.BytesIO()
                first_img_padded.save(pdf_buffer, format="PDF", save_all=True, append_images=image_list)
                pdf_buffer.seek(0)
                
                st.balloons() # Ekranda vizual şar animasiyası üçün
                st.success("✅ PDF uğurla yaradıldı!")
                
                # Yükləmə (Download) düyməsi
                st.download_button(
                    label="📥 PDF-i Kompüterə Yüklə",
                    data=pdf_buffer,
                    file_name="birlestirilmis_fayl.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Xəta baş verdi: {e}")