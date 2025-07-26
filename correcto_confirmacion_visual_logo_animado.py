
import streamlit as st
import io
from reportlab.pdfgen import canvas
from email.message import EmailMessage
import smtplib
import ssl

st.set_page_config(page_title="Presupuesto Innovation Crafters", layout="centered")

<style>
    body {
        font-family: 'Segoe UI', sans-serif;
        color: #333;
    }
    .stButton>button {
        background-color: #00856f;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1.2em;
    }
    .stDownloadButton>button {
        background-color: #002c2c;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1.2em;
    }
    .stTextInput>div>input {
        border-radius: 8px;
        border: 1px solid #00856f;
    }

<style>
    .fade-in {
        animation: fadeIn ease 2s;
        -webkit-animation: fadeIn ease 2s;
        -moz-animation: fadeIn ease 2s;
        -o-animation: fadeIn ease 2s;
        -ms-animation: fadeIn ease 2s;
    }

    @keyframes fadeIn {
        0% {opacity:0;}
        100% {opacity:1;}
    }
    @-moz-keyframes fadeIn {
        0% {opacity:0;}
        100% {opacity:1;}
    }
    @-webkit-keyframes fadeIn {
        0% {opacity:0;}
        100% {opacity:1;}
    }
    @-o-keyframes fadeIn {
        0% {opacity:0;}
        100% {opacity:1;}
    }
    @-ms-keyframes fadeIn {
        0% {opacity:0;}
        100% {opacity:1;}
    }
</style>

</style>


st.image('https://raw.githubusercontent.com/innovationcrafters/assets/main/logo_innovation_crafters.png', width=200)
st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
st.title("Presupuesto personalizado Innovation Crafters")

nombre = st.text_input("Nombre del cliente", "")
empresa = st.text_input("Nombre de la empresa", "")
direccion = st.text_input("Dirección", "")
telefono = st.text_input("Teléfono", "")
email = st.text_input("Correo electrónico", "")

modalidad = st.selectbox("Selecciona modalidad", ["Standard", "Premium", "Platino"])
kilos = st.number_input("Cantidad total de kilos", min_value=0.0, step=0.1)

# Simulamos la generación de PDF
def generar_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 800, f"Presupuesto para {nombre}")
    c.drawString(100, 780, f"Empresa: {empresa}")
    c.drawString(100, 760, f"Modalidad: {modalidad}")
    c.drawString(100, 740, f"Kilos: {kilos}")
    c.save()
    buffer.seek(0)
    return buffer

if st.button("📩 Enviar y Descargar Presupuesto"):
    pdf_buffer = generar_pdf()

    try:
        SMTP_SERVER = "mail.innovationcbd.es"
        SMTP_PORT = 465
        SMTP_USER = "crafters@innovationcbd.es"
        SMTP_PASS = "(ArgentinA2013)"
        COPIA_EMPRESA = "hola@innovationcbd.es"

        email_msg = EmailMessage()
        email_msg["Subject"] = "Presupuesto personalizado de Innovation Crafters"
        email_msg["From"] = SMTP_USER
        email_msg["To"] = email
        email_msg["Bcc"] = COPIA_EMPRESA
        email_msg.set_content(f"""Hola {nombre},

Adjuntamos tu presupuesto personalizado.

Un saludo,
Equipo Innovation Crafters
""")
        email_msg.add_attachment(pdf_buffer.getvalue(), maintype="application", subtype="pdf", filename="presupuesto_cbd.pdf")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(email_msg)

        st.success("📧 Presupuesto enviado automáticamente por email al cliente y a la empresa.")
        st.markdown("## ✅ ¡Gracias por tu solicitud!")
        st.markdown("Hemos recibido su petición correctamente. Nuestro departamento se pondrá en contacto con la mayor brevedad posible.")
        if st.button("🔁 Volver al inicio"):
            st.experimental_rerun()

    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {str(e)}")

    st.download_button("📄 Descargar PDF", key='descargar_pdf_button', data=pdf_buffer.getvalue(), file_name="presupuesto_cbd.pdf")

st.markdown("</div>", unsafe_allow_html=True)