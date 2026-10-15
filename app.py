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
    "Şəkilləri yükləyin, sırasını tənzimləyin və kənar boşluqlu PDF əldə edin."
)

# Ayarlar (Sidebar)
st.sidebar.header("⚙️ Ayarlar")
padding_input = st.sidebar.slider(
    "Kənar boşluq (Padding) ölçüsü:", min_value=0, max_value=100, value=40, step=5
)

# Sıralama üsulu seçimi
sort_method = st.sidebar.radio(
    "Sıralama üsulu:",
    [
        "Avtomatik (Adındakı rəqəmə görə)",
        "Yüklənmə ardıcıllığı",
        "Əllə nömrələmə (Prioritet)",
    ],
)

# Fayl yükləmə komponenti
uploaded_files = st.file_uploader(
    "Şəkilləri seçin və ya bura sürükləyin",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
  st.success(f"{len(uploaded_files)} şəkil seçildi.")

  # 1. Avtomatik sıralama
  if sort_method == "Avtomatik (Adındakı rəqəmə görə)":
    sorted_files = sorted(
        uploaded_files, key=lambda x: get_digit_from_name(x.name)
    )

  # 2. Yüklənmə ardıcıllığı
  elif sort_method == "Yüklənmə ardıcıllığı":
    sorted_files = uploaded_files

  # 3. Əllə nömrələmə (İstifadəçi sıra nömrəsi seçir + şəkillərin kiçik önizləməsi)
  else:
    st.subheader("🔀 Sıralama və Önizləmə")
    st.write(
        "Hər şəklin qarşısındakı rəqəmi dəyişərək ardıcıllığı təyin edin:"
    )

    file_order_dict = {}

    for i, file in enumerate(uploaded_files):
      col_img, col_name, col_order = st.columns([1, 3, 1])

      with col_img:
        # Kiçik önizləmə şəkli (100px enində)
        img = Image.open(file)
        st.image(img, width=100)

      with col_name:
        st.text(f"📷 {file.name}")

      with col_order:
        # Sıra nömrəsi təyini
        order_index = st.number_input(
            "Sıra",
            min_value=1,
            max_value=len(uploaded_files),
            value=i + 1,
            key=f"order_{file.name}_{i}",
        )
        file_order_dict[file] = order_index

    # Seçilmiş sıra nömrələrinə görə faylları sıralayırıq
    sorted_files = sorted(uploaded_files, key=lambda x: file_order_dict[x])

  # Əgər əllə nömrələmə seçilməyibsə, yekun sıranı göstərən kiçik qalereya
  if sort_method != "Əllə nömrələmə (Prioritet)":
    st.subheader("🖼️ Yekun Ardıcıllıq")
    cols = st.columns(4)  # 4 sütunlu kiçik qalereya
    for idx, file in enumerate(sorted_files):
      with cols[idx % 4]:
        img = Image.open(file)
        st.image(img, use_container_width=True, caption=f"{idx+1}. {file.name}")

  st.divider()

  # PDF Hazırlama Düyməsi
  if st.button("🚀 PDF Hazırla"):
    with st.spinner("Şəkillər emal olunur, xahiş edirik gözləyin..."):
      try:
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
