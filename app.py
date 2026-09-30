from hashlib import sha256
from pathlib import Path

import streamlit as st

from signature_pad import signature_pad
from signing import SigningError, find_locations, load_document, sign_document, signature_png


st.set_page_config(page_title="Firmar un Word", page_icon="✍️", layout="centered")
st.html("""
<style>
  .stMainBlockContainer { max-width: 760px; padding-top: 3rem; padding-bottom: 3rem; }
  h1 { font-family: Georgia, 'Times New Roman', serif; font-weight: 400 !important; letter-spacing: -.035em; }
  [data-testid="stFileUploader"] { margin-top: .5rem; }
  [data-testid="stFileUploaderDropzone"] { border: 1px dashed #aebdd0; background: #f7f9fc; }
  @media (max-width: 600px) { .stMainBlockContainer { padding-top: 1.5rem; } }
</style>
""")
st.title("Firmar un Word")


def clear_result():
    st.session_state.pop("signed_document", None)
    st.session_state.pop("signed_inputs", None)


def reset_document():
    clear_result()
    st.session_state["document_generation"] = st.session_state.get("document_generation", 0) + 1
    for key in ("document", "document_id", "search_phrase", "selected_location"):
        st.session_state.pop(key, None)


uploaded = st.file_uploader(
    "Cargar documento Word", type=["docx"], max_upload_size=10,
    help="Tu propio archivo .docx, de hasta 10 MB.",
    key="uploaded_word", on_change=reset_document,
)
if uploaded is None:
    st.stop()

original = uploaded.getvalue()
document_id = sha256(original).hexdigest()
try:
    if st.session_state.get("document_id") != document_id:
        st.session_state.document = load_document(original)
        st.session_state.document_id = document_id
    document = st.session_state.document
except SigningError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("Dónde va tu firma")
with st.expander("Buscar otro texto"):
    phrase = st.text_input(
        "Texto que indica dónde firmar", value="firma", key="search_phrase", on_change=clear_result,
        help="Buscamos esta palabra o frase en los párrafos y las tablas de tu Word.",
    )

locations = find_locations(document, phrase)
if not locations:
    clear_result()
    st.info("No encontramos ese texto. Abrí «Buscar otro texto» e ingresá el rótulo que aparece en tu Word.")
    st.caption("Se buscan párrafos y tablas del documento; no cuadros de texto, encabezados ni pies de página.")
    st.stop()

by_index = {location.index: location for location in locations}
if len(locations) > 1:
    if st.session_state.get("selected_location") not in by_index:
        st.session_state.selected_location = None
    selection = st.selectbox(
        "Encontramos varios lugares. Elegí dónde firmar", options=list(by_index), index=None,
        format_func=lambda index: f"{by_index[index].label[:90]} · ubicación {list(by_index).index(index) + 1}",
        placeholder="Seleccionar ubicación", key="selected_location", on_change=clear_result,
    )
    if selection is None:
        st.stop()
    location = by_index[selection]
else:
    location = locations[0]

with st.container(border=True):
    st.caption(location.place)
    st.text(location.context)
st.caption("La firma se insertará encima del párrafo elegido, conservando el texto. Puede cambiar la paginación del Word.")

st.subheader("Tu firma")
pad_key = f"signature_{st.session_state.get('document_generation', 0)}_{document_id}"
previous_pad = st.session_state.get(pad_key, {})
pad = signature_pad(
    key=pad_key, data={"initial": previous_pad.get("signature")},
    default={"signature": None}, on_signature_change=clear_result,
)
png = None
try:
    if pad.signature:
        png = signature_png(pad.signature)
except SigningError as exc:
    st.error(str(exc))

inputs = (document_id, location.index, sha256(png).hexdigest() if png else None)
if st.session_state.get("signed_inputs") != inputs:
    clear_result()

if st.button("Preparar documento firmado", type="primary", disabled=png is None, width="stretch"):
    try:
        with st.spinner("Preparando tu Word…"):
            st.session_state.signed_document = sign_document(original, location.index, png)
            st.session_state.signed_inputs = inputs
    except SigningError as exc:
        st.error(str(exc))

if st.session_state.get("signed_document") is not None:
    st.success("Tu documento firmado está listo.")
    st.download_button(
        "Descargar Word firmado", data=st.session_state.signed_document,
        file_name=f"{Path(uploaded.name).stem}_firmado.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary", width="stretch", on_click="ignore",
    )
st.caption("Firma manuscrita insertada como imagen. El documento se procesa en esta sesión, sin guardarlo en una base de datos.")
