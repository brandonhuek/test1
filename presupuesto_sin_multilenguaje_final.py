
import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image
import smtplib
import ssl
from email.message import EmailMessage

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
    </style>
""", unsafe_allow_html=True)

if "pagina" not in st.session_state:
    st.session_state.pagina = "formulario"

if st.session_state.pagina == "confirmacion":
    st.image("logo_innovation_crafters.png", width=100)
    st.markdown('<div class="confirmacion">✅ ¡Gracias por tu solicitud!<br>Hemos recibido tu petición correctamente.<br>Nos pondremos en contacto contigo muy pronto.</div>', unsafe_allow_html=True)
    st.download_button("📄 Descargar PDF", key='descargar_pdf_button_final', data=st.session_state.pdf, file_name="presupuesto_cbd.pdf")
    if st.button("🔁 Volver al inicio"):
        st.session_state.pagina = "formulario"
        st.experimental_rerun()
    st.stop()

st.image("logo_innovation_crafters.png", width=200)
st.title("Presupuesto personalizado Innovation Crafters")

nombre = st.text_input("Nombre")
empresa = st.text_input("Empresa")
direccion = st.text_input("Dirección")
telefono = st.text_input("Teléfono")
email = st.text_input("Email")
observaciones = st.text_area("Observaciones")

modalidad = st.selectbox("Modalidad", ["Standard", "Premium", "Platino"])

st.subheader("Cantidad de bolsas por formato")
formatos = ["1g", "2g", "3g", "5g", "10g", "20g", "50g", "100g"]
bolsas = {}
total_gramos = 0
for formato in formatos:
    cantidad = st.number_input(f"Bolsas de {formato}", key=f"bolsas_{formato}", min_value=0, value=0, step=10)
    bolsas[formato] = cantidad
    gramos = int(formato.replace("g", "")) * cantidad
    total_gramos += gramos

total_kg = total_gramos / 1000
st.markdown(f"**Total: {total_gramos}g ({total_kg:.2f} kg)**")

coste_bolsa_unitario = {
    "1g": 0.45, "2g": 0.45, "3g": 0.45,
    "5g": 0.50, "10g": 0.50, "20g": 0.50,
    "50g": 0.65, "100g": 0.65
}
mano_obra_precio = {"Standard": 300, "Premium": 275, "Platino": 300}
minimo_kg = {"Standard": 3.0, "Premium": 2.0, "Platino": 0.5}

if total_kg < minimo_kg[modalidad]:
    st.error(f"❌ El mínimo para la modalidad '{modalidad}' es de {minimo_kg[modalidad]} kg")
    st.stop()

precio_mano_obra = mano_obra_precio[modalidad] * total_kg
coste_total_bolsas = 0.0
if modalidad != "Premium":
    for formato, cantidad in bolsas.items():
        coste_total_bolsas += cantidad * coste_bolsa_unitario[formato]

tipo_envio = st.radio("Días de producción estimada", ["Standard (3-5 días hábiles + transporte)", "Express (3 días hábiles + transporte)"])
recargo_eq = st.selectbox("¿Recargo de equivalencia (5,2%)?", ["No", "Sí"])
imagenes = st.file_uploader("📸 Sube tus imágenes del producto", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

envio = 50 * total_kg if "Express" in tipo_envio else 5
base = precio_mano_obra + coste_total_bolsas + envio
recargo = 0.052 * base if recargo_eq == "Sí" else 0
iva = 0.21 * (base + recargo)
total = base + recargo + iva

st.markdown(f"### Total presupuesto: {total:.2f} € (IVA incluido)")

if not all([nombre, empresa, direccion, telefono, email]):
    st.warning("Por favor, completa todos los campos obligatorios.")
    st.stop()

def generar_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    try:
        c.drawImage("logo_innovation_crafters.png", 2 * cm, y - 2 * cm, width=4 * cm, preserveAspectRatio=True)
        y -= 3 * cm
    except:
        y -= 2 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "🧾 Datos del cliente")
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)
    for linea in [
        f"Nombre: {nombre}", f"Empresa: {empresa}", f"Dirección: {direccion}",
        f"Teléfono: {telefono}", f"Email: {email}", f"Observaciones: {observaciones}"
    ]:
        c.drawString(2 * cm, y, linea)
        y -= 0.4 * cm

    y -= 0.3 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "📦 Detalles del presupuesto:")
    y -= 0.5 * cm
    detalles = [
        f"Modalidad: {modalidad}", f"Total kg: {total_kg:.2f}",
        f"Coste bolsas: {coste_total_bolsas:.2f} €", f"Mano de obra: {precio_mano_obra:.2f} €",
        f"Envío: {envio:.2f} €", f"Recargo: {recargo:.2f} €",
        f"IVA: {iva:.2f} €", f"TOTAL: {total:.2f} €"
    ]
    for detalle in detalles:
        c.drawString(2 * cm, y, detalle)
        y -= 0.4 * cm

    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Detalle de bolsas:")
    y -= 0.4 * cm
    for formato, cantidad in bolsas.items():
        if cantidad > 0:
            c.drawString(2.5 * cm, y, f"{formato}: {cantidad} bolsas")
            y -= 0.35 * cm

    y -= 1 * cm
    for line in [
        "Inversiones Brandon e Hijos SL",
        "Calle Anselm Clavé 7, 17300, Blanes, Gerona",
        "CIF: B42761262",
        "IBAN: ES23 2100 0405 3402 0028 5866",
        "Pago: 60% por adelantado, 40% al salir el producto"
    ]:
        c.drawString(2 * cm, y, line)
        y -= 0.4 * cm

    if imagenes:
        c.showPage()
        y = height - 2 * cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, "📸 Imágenes del producto")
        y -= 0.5 * cm
        for imagen in imagenes[:4]:
            try:
                img = Image.open(imagen)
                img.thumbnail((400, 400))
                img_io = BytesIO()
                img.save(img_io, format='PNG')
                img_io.seek(0)
                img_reader = ImageReader(img_io)

                if y < 8 * cm:
                    c.showPage()
                    y = height - 2 * cm

                c.drawImage(img_reader, 2 * cm, y - 6 * cm, width=6 * cm, preserveAspectRatio=True)
                y -= 7 * cm
            except:
                continue

    c.save()
    buffer.seek(0)
    return buffer

if st.button("📄 Descargar presupuesto"):
    pdf = generar_pdf()

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
        email_msg.set_content(f'''
Hola {nombre},

Adjuntamos tu presupuesto personalizado.

Un saludo,
Equipo Innovation Crafters
''')
        email_msg.add_attachment(pdf.getvalue(), maintype="application", subtype="pdf", filename="presupuesto_cbd.pdf")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(email_msg)

    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {str(e)}")

    st.session_state.pdf = pdf
    st.session_state.pagina = "confirmacion"
    st.experimental_rerun()
