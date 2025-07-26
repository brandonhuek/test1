
import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image

st.set_page_config(page_title="Presupuesto personalizado Innovation Crafters", layout="centered")

# CSS personalizado
st.markdown("""
    <style>
    .confirmacion {
        background-color: #e6ffe6;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #00cc66;
        text-align: center;
        font-size: 18px;
    }
    .logo-animado {
        animation: rotar 4s infinite linear;
        height: 100px;
    }
    @keyframes rotar {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# Estado de la página
if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

# Página de confirmación
if st.session_state.pagina == "confirmacion":
    st.image("logo_innovation_crafters.png", width=100)
    st.markdown('<div class="confirmacion">✅ ¡Gracias por tu solicitud!<br>Hemos recibido tu petición correctamente.<br>Nos pondremos en contacto contigo muy pronto.</div>', unsafe_allow_html=True)
    st.download_button("📄 Descargar PDF", key='descargar_pdf_button_final', data=st.session_state.pdf, file_name="presupuesto_cbd.pdf")
    if st.button("🔁 Volver al inicio"):
        st.session_state.pagina = "formulario"
        st.experimental_rerun()
    st.stop()

# Resto del formulario básico
st.image("logo_innovation_crafters.png", width=200)
st.title("Presupuesto personalizado Innovation Crafters")
nombre = st.text_input("Nombre")
empresa = st.text_input("Empresa")
direccion = st.text_input("Dirección")
telefono = st.text_input("Teléfono")
email = st.text_input("Email")

# Validación básica
if not all([nombre, empresa, direccion, telefono, email]):
    st.warning("Por favor, completa todos los campos obligatorios.")
    st.stop()

def generar_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Presupuesto para {nombre} - {empresa}")
    c.drawString(100, 780, f"Dirección: {direccion}")
    c.drawString(100, 760, f"Teléfono: {telefono}")
    c.drawString(100, 740, f"Email: {email}")
    c.drawString(100, 700, "Este es un presupuesto generado automáticamente.")
    c.save()
    buffer.seek(0)
    return buffer

if st.button("📄 Descargar presupuesto"):
    pdf = generar_pdf()
    st.session_state.pdf = pdf
    st.session_state.pagina = "confirmacion"
    st.experimental_rerun()
