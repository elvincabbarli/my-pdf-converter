import io
import re
from PIL import Image
import streamlit as st

# Səhifə nizamlamaları
st.set_page_config(
    page_title="Şəkil -> PDF Çevirici", page_icon="🖼️", layout="centered"
)


def get_digit_from_name(filename):
  match = re.search(r"\d+", filename)
  return int(match.group()) if match else 0


def add_padding_to_image(img, padding_size=40):
  width, height = img.size
  new_width = width + padding_size * 2
  new_height = height + padding_size * 2
  padded_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
  padded_img.paste(img, (padding_size, padding_size))
  return padded_img


# Veb İnterfeys Dizaynı
st.title("🖼️ Şəkilləri PDF-ə Çevir")
st.write(
    "Şəkilləri yükləyin, düymələrdən istifadə edərək sıralarını dəyişin və PDF"
    " əldə edin."
)

# Ayarlar (Sidebar)
st.sidebar.header("⚙️ Ayarlar")
padding_input = st.sidebar.slider(
    "Kənar boşluq (Padding) ölçüsü:", min_value=0, max_value=100, value=40, step=5
)

# Fayl yükləmə komponenti
uploaded_files = st.file_uploader(
    "Şəkilləri seçin və ya bura sürükləyin",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
  # Session state-də faylların sırasını saxlayırıq ki, düyməyə basanda yaddan çıxmasın
  if (
      "file_order" not in st.session_state
      or set(st.session_state.file_order) != set(uploaded_files)
  ):
    # İlkin olaraq adındakı rəqəmə görə sıralayırıq
    st.session_state.file_order = sorted(
        uploaded_files, key=lambda x: get_digit_from_name(x.name)
    )

  st.subheader("📋 Şəkillərin Ardıcıllığı və Dəyişdirilməsi")
  st.info(
      "Hər şəklin yanında kiçik önizləməni və `⬆️` / `⬇️` düymələri ilə yeri"
      " dəyişə bilərsiniz:"
  )

  # Hər bir şəkli sətr olaraq göstəririk
  for i, file in enumerate(st.session_state.file_order):
    col_img, col_info, col_up, col_down = st.columns([1, 3, 1, 1])

    with col_img:
      img = Image.open(file)
      st.image(img, width=70)  # Kiçik önizləmə

    with col_info:
      st.text(f"Sıra: {i+1}\n{file.name}")

    with col_up:
      # Əgər ilk şəkil deyilsə, yuxarı qaldırmaq üçün düymə göstər
      if i > 0:
        if st.button("⬆️", key=f"up_{file.name}_{i}"):
          # Yuxarıdakı ilə yeri dəyişirik (Swap)
          st.session_state.file_order[i], st.session_state.file_order[i - 1] = (
              st.session_state.file_order[i - 1],
              st.session_state.file_order[i],
          )
          st.rerun()

    with col_down:
      # Əgər son şəkil deyilsə, aşağı salmaq üçün düymə göstər
      if i < len(st.session_state.file_order) - 1:
        if st.button("⬇️", key=f"down_{file.name}_{i}"):
          # Aşağıdakı ilə yeri dəyişirik (Swap)
          st.session_state.file_order[i], st.session_state.file_order[i + 1] = (
              st.session_state.file_order[i + 1],
              st.session_state.file_order[i],
          )
          st.rerun()

  st.divider()

  # PDF Hazırlama Düyməsi
  if st.button("🚀 PDF Hazırla"):
    with st.spinner("Şəkillər emal olunur, xahiş edirik gözləyin..."):
      try:
        sorted_files = st.session_state.file_order

        # İlk şəkli hazırlayırıq
        first_img = Image.open(sorted_files[0]).convert("RGB")
        first_img_padded = add_padding_to_image(first_img, padding_input)

        # Digər şəkilləri hazırlayırıq
        image_list = []
        for file in sorted_files[1:]:
          img = Image.open(file).convert("RGB")
          img_padded = add_padding_to_image(img, padding_input)
          image_list.append(img_padded)

        # PDF-i RAM-da saxlamaq
        pdf_buffer = io.BytesIO()
        first_img_padded.save(
            pdf_buffer, format="PDF", save_all=True, append_images=image_list
        )
        pdf_buffer.seek(0)

        st.balloons()
        st.success("✅ PDF uğurla yaradıldı!")

        # Yükləmə düyməsi
        st.download_button(
            label="📥 PDF-i Kompüterə Yüklə",
            data=pdf_buffer,
            file_name="birlestirilmis_fayl.pdf",
            mime="application/pdf",
        )

      except Exception as e:
        st.error(f"Xəta baş verdi: {e}")
