import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import ssl
import re
import datetime # Importar datetime para la fecha del presupuesto

# --- Importaciones para Google Sheets ---
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuración de la página general ---
st.set_page_config(page_title="Innovation Crafters", layout="centered")

# Logo directo
st.image("logo_innovation_crafters.png", width=200)

# --- Multilenguaje (se mantiene global) ---
idioma = st.selectbox("🌐 Elige idioma / Select language", ["Español", "English"])
lang = {
    "Español": {
        "datos_cliente": "Datos fiscales del Cliente",
        "nombre": "Nombre completo o razón social",
        "empresa": "Empresa (opcional)",
        "cif_nif": "CIF/NIF",
        "telefono": "Teléfono de contacto",
        "email": "Email",
        "observaciones": "Observaciones",
        "modalidad": "Modalidad",
        "bolsas": "Indica cuántas bolsas quieres por cada formato:",
        "minimo": "El mínimo para la modalidad",
        "tipo_envio": "Días de producción estimada",
        "recargo_eq": "¿Recargo de equivalencia (5,2%)?",
        "imagenes": "📸 Sube tus imágenes del producto",
        "total_presupuesto": "Total presupuesto",
        "descargar": "📄 Descargar presupuesto",
        "advertencia_campos_obligatorios": "Por favor, completa todos los campos obligatorios (*).",
        "advertencia_email_invalido": "Por favor, introduce un email válido.",
        "advertencia_minimo_botellas": "⚠️ El pedido mínimo de botellas es 100 unidades.",
        "advertencia_minimo_extracciones": "⚠️ El pedido mínimo de frascos de extracciones es 150 unidades.",
        "asunto_email": "Tu Presupuesto Personalizado de Innovation Crafters",
        "cuerpo_email_html": """
        <html>
            <body>
                <p>Estimado/a cliente,</p>
                <p>Adjunto encontrarás tu presupuesto personalizado de Innovation Crafters. Nos pondremos en contacto contigo a la mayor brevedad posible para discutir los detalles.</p>
                <p>Gracias por tu interés.</p>
                <p>Atentamente,<br>El equipo de Innovation Crafters</p>
                <p><img src="cid:logo_innovation_crafters" alt="Innovation Crafters Logo" style="width:150px;height:auto;"></p>
            </body>
        </html>
        """,
        "cuerpo_email_plain": "Estimado/a cliente,\n\nAdjunto encontrarás tu presupuesto personalizado de Innovation Crafters. Nos pondremos en contacto contigo a la mayor brevedad posible para discutir los detalles.\n\nGracias por tu interés.\n\nAtentamente,\nEl equipo de Innovation Crafters",
        "error_email": "❌ Error al enviar el correo electrónico. Por favor, inténtalo de nuevo o contacta con soporte.",
        "exito_email": "✅ Presupuesto enviado y correo electrónico enviado con éxito.",
        "advertencia_minimo_aceites_extracciones": "Para aceites o extracciones, debes pedir al menos 100 botellas o 150 frascos para descargar el presupuesto.",
        "misma_direccion": "Usar misma dirección que datos fiscales",
        "modalidad_standard_desc": """
            **Standard:**
            *   **Empaquetado de productos:** SOLO CBD
            *   **Producto a Granel:** A negociar con la marca
            *   **Marca de las bolsas:** Cannabis Innovation CBD
        """,
        "modalidad_premium_desc": """
            **Premium:**
            *   **Empaquetado de productos:** SOLO CBD
            *   **Producto a Granel:** A negociar con la marca o tu propio producto a granel
            *   **Marca de las bolsas:** Tu propia Marca (deberás enviarnos tus propias bolsas, recuerda que pueden existir cargos adicionales dependiendo el producto a granel)
        """,
        "modalidad_platino_desc": """
            **Platino:**
            *   **Empaquetado de productos:** SOLO (Nano9, Nano10, Nano XXX, y moléculas exclusivas de la marca)
            *   **Producto a Granel:** A negociar con la marca
            *   **Marca de las bolsas:** Cannabis Innovation CBD
        """,
        "granel_pregunta": "¿Cómo gestionarás el producto a granel?",
        "granel_envio_propio": "Lo enviaré yo mismo (asumo costes de envío y posibles aranceles)",
        "granel_negociar": "Lo voy a negociar con Innovation Crafters",
        "pais": "País",
        "iva_anulado_info": "IVA anulado por ser cliente intracomunitario.",
        "recargo_anulado_info": "Recargo de equivalencia anulado (solo aplica en España)."
    },
    "English": {
        "datos_cliente": "Customer Tax Information",
        "nombre": "Full Name or Company Name",
        "empresa": "Company (optional)",
        "cif_nif": "Tax ID (CIF/NIF)",
        "telefono": "Contact Phone",
        "email": "Email",
        "observaciones": "Notes",
        "modalidad": "Packaging Option",
        "bolsas": "Enter how many bags you want per format:",
        "minimo": "Minimum for selected option is",
        "tipo_envio": "Estimated production days",
        "recargo_eq": "Equivalence surcharge (5.2%)?",
        "imagenes": "📸 Upload your product images",
        "total_presupuesto": "Total budget",
        "descargar": "📄 Download PDF",
        "advertencia_campos_obligatorios": "Please complete all required fields (*).",
        "advertencia_email_invalido": "Please enter a valid email address.",
        "advertencia_minimo_botellas": "⚠️ The minimum order for bottles is 100 units.",
        "advertencia_minimo_extracciones": "⚠️ The minimum order for extraction jars is 150 units.",
        "asunto_email": "Your Personalized Quote from Innovation Crafters",
        "cuerpo_email_html": """
        <html>
            <body>
                <p>Dear Customer,</p>
                <p>Attached you will find your personalized quote from Innovation Crafters. We will contact you as soon as possible to discuss the details.</p>
                <p>Thank you for your interest.</p>
                <p>Sincerely,<br>The Innovation Crafters Team</p>
                <p><img src="cid:logo_innovation_crafters" alt="Innovation Crafters Logo" style="width:150px;height:auto;"></p>
            </body>
        </html>
        """,
        "cuerpo_email_plain": "Dear Customer,\n\nAttached you will find your personalized quote from Innovation Crafters. We will contact you as soon as possible to discuss the details.\n\nThank you for your interest.\n\nSincerely,\nThe Innovation Crafters Team",
        "error_email": "❌ Error sending email. Please try again or contact support.",
        "exito_email": "✅ Quote sent and email successfully delivered.",
        "advertencia_minimo_aceites_extracciones": "For oils or extractions, you must order at least 100 bottles or 150 jars to download the quote.",
        "misma_direccion": "Use same address as tax information",
        "modalidad_standard_desc": """
            **Standard:**
            *   **Product Packaging:** CBD ONLY
            *   **Bulk Product:** To be negotiated with the brand
            *   **Bag Brand:** Cannabis Innovation CBD
        """,
        "modalidad_premium_desc": """
            **Premium:**
            *   **Product Packaging:** CBD ONLY
            *   **Bulk Product:** To be negotiated with the brand or your own bulk product
            *   **Bag Brand:** Your own Brand (you will need to send us your own bags, additional charges may apply depending on the bulk product)
        """,
        "modalidad_platino_desc": """
            **Platinum:**
            *   **Product Packaging:** ONLY (Nano9, Nano10, Nano XXX, and exclusive brand molecules)
            *   **Bulk Product:** To be negotiated with the brand
            *   **Bag Brand:** Cannabis Innovation CBD
        """,
        "granel_pregunta": "How will you manage the bulk product?",
        "granel_envio_propio": "I will send it myself (I assume shipping costs and possible duties)",
        "granel_negociar": "I will negotiate it with Innovation Crafters"
    }
}[idioma]

# Lista de países de la Unión Europea (simplificada para el ejemplo)
EU_COUNTRIES = [
    "España", "Alemania", "Francia", "Italia", "Portugal", "Bélgica", "Países Bajos",
    "Luxemburgo", "Irlanda", "Austria", "Finlandia", "Suecia", "Dinamarca", "Grecia",
    "Polonia", "República Checa", "Hungría", "Eslovaquia", "Eslovenia", "Croacia",
    "Rumanía", "Bulgaria", "Chipre", "Malta", "Estonia", "Letonia", "Lituania"
]

# --- Funciones de validación (se mantienen globales) ---
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def is_valid_nif(nif):
    return len(nif) >= 8 and len(nif) <= 9 and nif.isalnum()

# --- Función para enviar el correo electrónico (se mantiene global) ---
def enviar_email_con_adjunto(destinatario_email, pdf_buffer_data, nombre_archivo_pdf, asunto, cuerpo_mensaje_html, cuerpo_mensaje_plain):
    try:
        # Asegúrate de que estas variables estén configuradas en st.secrets
        # Para Streamlit Cloud, esto se hace en la sección "Secrets"
        # Para desarrollo local, puedes usar un archivo .streamlit/secrets.toml
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASS"]
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = st.secrets["SMTP_PORT"]

        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = destinatario_email
        msg['Subject'] = asunto

        msg.attach(MIMEText(cuerpo_mensaje_plain, 'plain'))
        msg.attach(MIMEText(cuerpo_mensaje_html, 'html'))

        part_pdf = MIMEApplication(pdf_buffer_data, Name=nombre_archivo_pdf)
        part_pdf['Content-Disposition'] = f'attachment; filename="{nombre_archivo_pdf}"'
        msg.attach(part_pdf)

        try:
            with open("logo_innovation_crafters.png", "rb") as img_file:
                img_data = img_file.read()
            part_img = MIMEImage(img_data, name="logo_innovation_crafters.png")
            part_img.add_header('Content-ID', '<logo_innovation_crafters>')
            msg.attach(part_img)
        except FileNotFoundError:
            st.warning("Logo 'logo_innovation_crafters.png' no encontrado para incrustar en el email.")
        except Exception as e:
            st.warning(f"Error al incrustar el logo en el email: {e}")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error al enviar el correo: {e}")
        return False

# --- Función para generar el PDF (se mantiene global) ---
def generar_pdf(nombre, empresa, cif_nif, telefono, email, pais, direccion_fiscal, direccion_envio, observaciones,
                materia_prima, modalidad, unidades_botellas, unidades_extracciones, coste_botellas, coste_extracciones,
                precio_mano_obra, coste_total_bolsas, total_kg, bolsas, granel_gestion, tipo_envio, recargo, iva_aplicado, total, envio):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    try:
        logo_x = 1.5 * cm
        logo_y = height - 2.5 * cm
        logo_width = 3 * cm
        logo_height = 1.5 * cm
        c.drawImage("logo_innovation_crafters.png", logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
        y_start_content = height - 4 * cm
    except FileNotFoundError:
        st.warning("Logo 'logo_innovation_crafters.png' no encontrado para el PDF.")
        y_start_content = height - 2 * cm
    except Exception as e:
        st.warning(f"Error al cargar el logo para el PDF: {e}")
        y_start_content = height - 2 * cm

    y = y_start_content

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, lang["datos_cliente"])
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)
    for linea in [
        f"{lang['nombre']}: {nombre}",
        f"{lang['empresa']}: {empresa}",
        f"{lang['cif_nif']}: {cif_nif}",
        f"{lang['telefono']}: {telefono}",
        f"{lang['email']}: {email}",
        f"{lang['pais']}: {pais}",
        f"Dirección fiscal: {direccion_fiscal}",
        f"Dirección de envío: {direccion_envio}"
    ]:
        c.drawString(2 * cm, y, linea)
        y -= 0.4 * cm
    
    if observaciones:
        c.drawString(2 * cm, y, f"{lang['observaciones']}: {observaciones}")
        y -= 0.4 * cm

    y -= 0.3 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "📦 Detalles del presupuesto:")
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)

    # Calcular IVA para el PDF
    base_imponible_para_iva = (coste_botellas + coste_extracciones + envio) if materia_prima == "Aceites CBD o Extracciones (Crumble, Isolado, Cristales)" else (precio_mano_obra + coste_total_bolsas + envio)
    iva_pdf = iva_aplicado * (base_imponible_para_iva + recargo)

    detalles = []
    if materia_prima == "Aceites CBD o Extracciones (Crumble, Isolado, Cristales)":
        detalles = [
            f"Botellas 10ml: {unidades_botellas} unidades - {coste_botellas:.2f} €",
            f"Frascos extracciones 3g: {unidades_extracciones} unidades - {coste_extracciones:.2f} €",
            f"Coste base productos: {(coste_botellas + coste_extracciones):.2f} €",
            f"Envío ({'Standard' if 'Standard' in tipo_envio else 'Express'}): {envio:.2f} €",
            f"Subtotal (Base + Envío): {(coste_botellas + coste_extracciones + envio):.2f} €",
            f"Recargo de equivalencia (5.2%): {recargo:.2f} €",
            f"IVA ({iva_aplicado*100:.0f}%): {iva_pdf:.2f} €", # Usar iva_pdf
            f"TOTAL: {total:.2f} €"
        ]
    else:
        detalles = [
            f"Modalidad: {modalidad}",
            f"Total kg: {total_kg:.2f} kg",
            f"Coste bolsas: {coste_total_bolsas:.2f} €",
            f"Mano de obra: {precio_mano_obra:.2f} €",
            f"Envío ({'Standard' if 'Standard' in tipo_envio else 'Express'}): {envio:.2f} €",
            f"Subtotal (Base + Envío): {(precio_mano_obra + coste_total_bolsas + envio):.2f} €",
            f"Recargo de equivalencia (5.2%): {recargo:.2f} €",
            f"IVA ({iva_aplicado*100:.0f}%): {iva_pdf:.2f} €", # Usar iva_pdf
            f"TOTAL: {total:.2f} €"
        ]
        if modalidad == "Premium" and granel_gestion:
            detalles.insert(2, f"Gestión de producto a granel: {granel_gestion}")

    for detalle in detalles:
        c.drawString(2 * cm, y, detalle)
        y -= 0.4 * cm

    if materia_prima == "Flores y Hachises" and bolsas:
        y -= 0.5 * cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, y, "Detalle de bolsas:")
        y -= 0.4 * cm
        c.setFont("Helvetica", 10)
        for formato, cantidad in bolsas.items():
            if cantidad > 0:
                c.drawString(2.5 * cm, y, f"{formato}: {cantidad} bolsas")
                y -= 0.35 * cm

    y -= 1 * cm
    c.setFont("Helvetica", 9)
    for line in [
        "Inversiones Brandon e Hijos SL",
        "Calle Anselm Clavé 7, 17300, Blanes, Gerona",
        "CIF: B42761262",
        "IBAN: ES23 2100 0405 3402 0028 5866",
        "Pago: 60% por adelantado, 40% al salir el producto"
    ]:
        c.drawString(2 * cm, y, line)
        y -= 0.4 * cm

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# --- Conexión a Google Sheets ---
@st.cache_resource(ttl=3600) # Cachea la conexión para evitar re-autenticación constante
def get_google_sheet_client():
    try:
        # Cargar las credenciales desde el archivo JSON
        # Para Streamlit Cloud, esto se hace en la sección "Secrets"
        # Para desarrollo local, puedes usar un archivo .streamlit/secrets.toml
        if "gcp_service_account" in st.secrets:
            # Para Streamlit Cloud, usa st.secrets
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], 
                                                                     ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
        else:
            # Para desarrollo local, usa el archivo credentials.json
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', 
                                                                     ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
        
        client = gspread.authorize(creds)
        return client
    except FileNotFoundError:
        st.error("Error: 'credentials.json' no encontrado. Asegúrate de que el archivo de credenciales de Google Sheets esté en la misma carpeta que tu script.")
        st.stop()
    except Exception as e:
        st.error(f"Error al autenticarse con Google Sheets: {e}")
        st.stop()

# Inicializar el cliente de Google Sheets
# Solo inicializar si no estamos en la página de inicio o quienes somos, para evitar errores si no se usa.
# Sin embargo, para simplificar, lo inicializamos globalmente y manejamos el error si falta el archivo.
gc = get_google_sheet_client()

# --- Función para guardar datos en Google Sheets ---
def guardar_presupuesto_en_sheets(datos_presupuesto):
    try:
        spreadsheet = gc.open("Presupuestos Innovation Crafters") # Nombre de tu hoja de cálculo
        worksheet = spreadsheet.sheet1 # O el nombre de tu hoja específica, ej. spreadsheet.worksheet("Hoja1")

        # Obtener los encabezados actuales de la hoja para asegurar el orden
        # Si la hoja está vacía, puedes definir los encabezados aquí
        if not worksheet.row_values(1): # Si la primera fila está vacía, asume que no hay encabezados
            headers = [
                "Fecha", "Nombre", "Empresa", "CIF/NIF", "Teléfono", "Email", "País",
                "Dirección Fiscal", "Dirección de Envío", "Observaciones",
                "Materia Prima", "Modalidad", "Unidades Botellas", "Unidades Extracciones",
                "Coste Botellas", "Coste Extracciones", "Precio Mano Obra", "Coste Total Bolsas",
                "Total Kg", "Bolsas (Detalle)", "Gestión Granel", "Tipo Envío",
                "Recargo Equivalencia", "IVA Aplicado", "Total Presupuesto"
            ]
            worksheet.append_row(headers)
        
        # Preparar la fila de datos
        row_data = [
            datos_presupuesto.get("Fecha", ""),
            datos_presupuesto.get("Nombre", ""),
            datos_presupuesto.get("Empresa", ""),
            datos_presupuesto.get("CIF/NIF", ""),
            datos_presupuesto.get("Teléfono", ""),
            datos_presupuesto.get("Email", ""),
            datos_presupuesto.get("País", ""),
            datos_presupuesto.get("Dirección Fiscal", ""),
            datos_presupuesto.get("Dirección de Envío", ""),
            datos_presupuesto.get("Observaciones", ""),
            datos_presupuesto.get("Materia Prima", ""),
            datos_presupuesto.get("Modalidad", ""),
            datos_presupuesto.get("Unidades Botellas", 0),
            datos_presupuesto.get("Unidades Extracciones", 0),
            datos_presupuesto.get("Coste Botellas", 0.0),
            datos_presupuesto.get("Coste Extracciones", 0.0),
            datos_presupuesto.get("Precio Mano Obra", 0.0),
            datos_presupuesto.get("Coste Total Bolsas", 0.0),
            datos_presupuesto.get("Total Kg", 0.0),
            str(datos_presupuesto.get("Bolsas (Detalle)", {})), # Convertir diccionario a string
            datos_presupuesto.get("Gestión Granel", ""),
            datos_presupuesto.get("Tipo Envío", ""),
            datos_presupuesto.get("Recargo Equivalencia", 0.0),
            datos_presupuesto.get("IVA Aplicado", 0.0),
            datos_presupuesto.get("Total Presupuesto", 0.0)
        ]
        
        worksheet.append_row(row_data)
        st.success("✅ Presupuesto guardado en Google Sheets.")
    except Exception as e:
        st.error(f"❌ Error al guardar el presupuesto en Google Sheets: {e}")


# --- Control de sesión para la navegación ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# --- Barra de navegación ---
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    if st.button("🏠 Inicio", key="nav_home"):
        st.session_state.current_page = "home"
with col_nav2:
    if st.button("ℹ️ Quiénes Somos", key="nav_quienes_somos"):
        st.session_state.current_page = "quienes_somos"
with col_nav3:
    if st.button("💰 Crear Presupuesto", key="nav_presupuesto"):
        st.session_state.current_page = "presupuesto"

st.markdown("---") # Separador visual

# --- Contenido de las páginas ---

if st.session_state.current_page == "home":
    st.title("Bienvenido a Innovation Crafters")
    st.markdown("""
    Explora nuestras soluciones de empaquetado y distribución para productos de CBD.
    """)
    if st.button("Conoce Quiénes Somos", key="btn_home_quienes"):
        st.session_state.current_page = "quienes_somos"
    if st.button("Crea tu Presupuesto", key="btn_home_presupuesto"):
        st.session_state.current_page = "presupuesto"

elif st.session_state.current_page == "quienes_somos":
    st.title("👋 ¡Hola! Somos Innovation Crafters")
    st.markdown("""
    En **Innovation Crafters**, somos un equipo apasionado y dedicado a transformar ideas en realidad. Nos especializamos en ofrecer soluciones innovadoras y personalizadas para el empaquetado y la distribución de productos de CBD, tanto flores como aceites y extracciones.

    ### Nuestra Misión
    Nuestra misión es ser el socio estratégico de nuestros clientes, proporcionando servicios de empaquetado de alta calidad que no solo protejan y presenten sus productos de manera excepcional, sino que también cumplan con todas las normativas y estándares del mercado. Nos esforzamos por la excelencia, la eficiencia y la satisfacción total del cliente.

    ### ¿Qué nos hace diferentes?
    *   **Personalización:** Entendemos que cada producto es único. Ofrecemos soluciones a medida que se adaptan a tus necesidades específicas de marca y empaquetado.
    *   **Calidad:** Utilizamos materiales de primera calidad y procesos rigurosos para asegurar que tus productos lleguen a su destino en perfectas condiciones.
    *   **Experiencia:** Contamos con un equipo experto en el sector del CBD, garantizando un manejo adecuado y profesional de tus materias primas.
    *   **Innovación:** Estamos constantemente explorando nuevas tecnologías y métodos para ofrecerte las soluciones más avanzadas del mercado.

    Creemos en construir relaciones duraderas basadas en la confianza y el compromiso. Permítenos ayudarte a llevar tus productos al siguiente nivel.

    ---
    """)
    st.markdown("## ¿Listo para empezar tu proyecto?")
    if st.button("🚀 Crear mi Presupuesto Personalizado", key="btn_quienes_presupuesto"):
        st.session_state.current_page = "presupuesto"

elif st.session_state.current_page == "presupuesto":
    st.title("💰 Presupuesto personalizado Innovation Crafters")

    # --- Control de sesión para redirigir si ya se ha enviado el presupuesto ---
    if "presupuesto_enviado" not in st.session_state:
        st.session_state.presupuesto_enviado = False
    if "pdf_data_for_download" not in st.session_state:
        st.session_state.pdf_data_for_download = None

    if st.session_state.presupuesto_enviado:
        st.success("✅ ¡Gracias por tu solicitud!")
        st.write("Hemos recibido su petición correctamente. Nuestro departamento se pondrá en contacto con la mayor brevedad posible.")

        if st.session_state.pdf_data_for_download:
            st.download_button(
                label="📥 Descargar tu presupuesto (PDF)",
                data=st.session_state.pdf_data_for_download,
                file_name="presupuesto_innovation_crafters.pdf",
                mime="application/pdf",
                key="download_button_confirmation_page"
            )

        if st.button("🔙 Volver al inicio", key="volver_inicio_presupuesto"):
            st.session_state.presupuesto_enviado = False
            st.session_state.pdf_data_for_download = None
            st.session_state.current_page = "home" # Redirigir a la página de inicio
        st.stop() # Detener la ejecución del resto del formulario

    # --- Inputs cliente ---
    st.subheader(lang["datos_cliente"])
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input(f"{lang['nombre']} *", key="nombre_fiscal")
            empresa = st.text_input(lang["empresa"], key="empresa_fiscal")
            cif_nif = st.text_input(f"{lang['cif_nif']} *", key="cif_nif")
        with col2:
            telefono = st.text_input(f"{lang['telefono']} *", key="telefono_fiscal")
            email = st.text_input(f"{lang['email']} *", key="email_fiscal")
            pais = st.selectbox(f"{lang['pais']} *", options=["España"] + sorted([p for p in EU_COUNTRIES if p != "España"]), index=0, key="pais_cliente")
        
        direccion_fiscal = st.text_area("Dirección fiscal completa *", 
                                    help="Calle, número, piso, código postal, población, provincia", 
                                    key="dir_fiscal")
        observaciones = st.text_area(lang["observaciones"])

    # --- Dirección de envío ---
    st.subheader("🚚 Dirección de Envío")
    misma_direccion = st.checkbox(lang["misma_direccion"], value=True, key="misma_dir")

    if misma_direccion:
        direccion_envio = direccion_fiscal
        st.info("✅ Se usará la dirección fiscal como dirección de envío")
    else:
        direccion_envio = st.text_area("Dirección de envío completa *", 
                                    help="Calle, número, piso, código postal, población, provincia",
                                    key="dir_envio")

    # --- Nueva sección: Materia prima a Empaquetar ---
    st.subheader("🌿 Materia prima a Empaquetar")
    materia_prima = st.selectbox("Selecciona el tipo de producto a empaquetar:", [
        "Flores y Hachises",
        "Aceites CBD o Extracciones (Crumble, Isolado, Cristales)"
    ])

    # --- Inicialización de variables para evitar NameError ---
    modalidad = None
    unidades_botellas = 0
    unidades_extracciones = 0
    coste_botellas = 0.0
    coste_extracciones = 0.0
    precio_mano_obra = 0.0
    coste_total_bolsas = 0.0
    total_kg = 0.0
    bolsas = {}
    granel_gestion = ""

    # --- Lógica condicional según la materia prima ---
    if materia_prima == "Flores y Hachises":
        modalidad = st.selectbox(lang["modalidad"], ["Standard", "Premium", "Platino"])

        if modalidad == "Standard":
            st.info(lang["modalidad_standard_desc"])
        elif modalidad == "Premium":
            st.info(lang["modalidad_premium_desc"])
            st.markdown(f"**{lang['granel_pregunta']}**")
            granel_gestion = st.radio("", [lang["granel_envio_propio"], lang["granel_negociar"]], key="granel_gestion_radio")
        elif modalidad == "Platino":
            st.info(lang["modalidad_platino_desc"])

        st.subheader(lang["bolsas"])
        formatos = ["1g", "2g", "3g", "5g", "10g", "20g", "50g", "100g"]

        coste_bolsa_unitario = {
            "1g": 0.45, "2g": 0.45, "3g": 0.45,
            "5g": 0.50, "10g": 0.50, "20g": 0.50,
            "50g": 0.65, "100g": 0.65
        }
        mano_obra_precio = {"Standard": 300, "Premium": 275, "Platino": 300}
        minimo_kg = {"Standard": 3.0, "Premium": 2.0, "Platino": 0.5}

        total_gramos = 0
        for formato in formatos:
            precio_unitario = coste_bolsa_unitario[formato]
            cantidad = st.number_input(f"Bolsas de {formato} ({precio_unitario:.2f} €/ud)", key=f"input_{formato}", min_value=0, value=0, step=10)
            bolsas[formato] = cantidad
            gramos = int(formato.replace("g", "")) * cantidad
            total_gramos += gramos

        total_kg = total_gramos / 1000
        st.markdown(f"**Total: {total_gramos}g ({total_kg:.2f} kg)**")

        if modalidad != "Premium":
            for formato, cantidad in bolsas.items():
                coste_total_bolsas += cantidad * coste_bolsa_unitario[formato]

        precio_mano_obra = mano_obra_precio[modalidad] * total_kg

        if total_kg < minimo_kg[modalidad]:
            st.error(f"❌ {lang['minimo']} '{modalidad}': {minimo_kg[modalidad]} kg")

    else: # Materia prima es "Aceites CBD o Extracciones"
        st.subheader("💧 Productos disponibles")

        unidades_botellas = st.number_input("Botellas de CBD 10ml con packaging incluido (2,50 €/ud)", min_value=0, step=10)
        unidades_extracciones = st.number_input("Frascos de extracciones 3g (2,30 €/ud)", min_value=0, step=10)

        if unidades_botellas > 0 and unidades_botellas < 100:
            st.warning(lang["advertencia_minimo_botellas"])
        if unidades_extracciones > 0 and unidades_extracciones < 150:
            st.warning(lang["advertencia_minimo_extracciones"])

        coste_botellas = unidades_botellas * 2.50
        coste_extracciones = unidades_extracciones * 2.30

        st.markdown(f"**Total productos: {(coste_botellas + coste_extracciones):.2f} €**")

    # --- Opciones de envío y recargo ---
    tipo_envio = st.radio(lang["tipo_envio"], ["Standard (3-5 días hábiles + transporte)", "Express (3 días hábiles + transporte)"])

    recargo_eq_disabled = (pais != "España")
    recargo_eq_value = "No"
    if not recargo_eq_disabled:
        recargo_eq_value = st.selectbox(lang["recargo_eq"], ["No", "Sí"])
    else:
        st.selectbox(lang["recargo_eq"], ["No", "Sí"], index=0, disabled=True)
        st.info(lang["recargo_anulado_info"])

    # --- Carga de imágenes ---
    imagenes = None
    if materia_prima == "Flores y Hachises" and modalidad == "Premium":
        imagenes = st.file_uploader(lang["imagenes"], type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    # --- Cálculo del presupuesto total ---
    envio = 0.0
    base = 0.0

    if materia_prima == "Aceites CBD o Extracciones (Crumble, Isolado, Cristales)":
        if "Standard" in tipo_envio:
            envio = 0.0
        else:
            envio = 0.20 * (unidades_botellas + unidades_extracciones)
        base = coste_botellas + coste_extracciones + envio
    else:
        envio = 50.0 * total_kg if "Express" in tipo_envio else 5.0
        base = precio_mano_obra + coste_total_bolsas + envio

    recargo = 0.052 * base if recargo_eq_value == "Sí" else 0.0

    iva_aplicado = 0.21
    iva_anulado_mensaje = ""
    if pais != "España" and pais in EU_COUNTRIES:
        iva_aplicado = 0.0
        iva_anulado_mensaje = lang["iva_anulado_info"]

    iva = iva_aplicado * (base + recargo)
    total = base + recargo + iva

    st.markdown(f"### {lang['total_presupuesto']}: {total:.2f} € (IVA incluido)")
    if iva_anulado_mensaje:
        st.info(iva_anulado_mensaje)

    # --- Lógica para habilitar/deshabilitar el botón de descarga ---
    mostrar_boton = True
    errores_validacion = []

    if not nombre:
        errores_validacion.append(f"El campo '{lang['nombre']}' es obligatorio.")
    if not cif_nif:
        errores_validacion.append(f"El campo '{lang['cif_nif']}' es obligatorio.")
    elif not is_valid_nif(cif_nif):
        errores_validacion.append(f"El formato de '{lang['cif_nif']}' no es válido.")
    if not telefono:
        errores_validacion.append(f"El campo '{lang['telefono']}' es obligatorio.")
    if not email:
        errores_validacion.append(f"El campo '{lang['email']}' es obligatorio.")
    elif not is_valid_email(email):
        errores_validacion.append(lang["advertencia_email_invalido"])
    if not direccion_fiscal:
        errores_validacion.append("La 'Dirección fiscal' es obligatoria.")
    if not direccion_envio:
        errores_validacion.append("La 'Dirección de envío' es obligatoria.")
    if not pais:
        errores_validacion.append(f"El campo '{lang['pais']}' es obligatorio.")

    if materia_prima == "Flores y Hachises":
        minimos = {"Standard": 3.0, "Premium": 2.0, "Platino": 0.5}
        minimo_requerido = minimos.get(modalidad, 0)
        if total_kg < minimo_requerido:
            errores_validacion.append(f"❌ No puedes descargar el presupuesto: la modalidad {modalidad} requiere mínimo {minimo_requerido} kg.")
        if modalidad == "Premium" and not granel_gestion:
            errores_validacion.append(f"Por favor, selecciona una opción para la gestión del producto a granel en la modalidad Premium.")

    elif materia_prima == "Aceites CBD o Extracciones (Crumble, Isolado, Cristales)":
        condicion_botellas_ok = unidades_botellas >= 100
        condicion_extracciones_ok = unidades_extracciones >= 150
        if not (condicion_botellas_ok or condicion_extracciones_ok):
            errores_validacion.append(lang["advertencia_minimo_aceites_extracciones"])

    if errores_validacion:
        mostrar_boton = False
        for error in errores_validacion:
            st.error(error)

    # --- Botón de descarga y envío ---
    if st.button(lang["descargar"], disabled=not mostrar_boton):
        with st.spinner("Generando presupuesto y enviando correo..."):
            # Pasar todos los parámetros necesarios a generar_pdf
            pdf_buffer = generar_pdf(nombre, empresa, cif_nif, telefono, email, pais, direccion_fiscal, direccion_envio, observaciones,
                                    materia_prima, modalidad, unidades_botellas, unidades_extracciones, coste_botellas, coste_extracciones,
                                    precio_mano_obra, coste_total_bolsas, total_kg, bolsas, granel_gestion, tipo_envio, recargo, iva_aplicado, total, envio)
            
            pdf_data = pdf_buffer.getvalue()
            file_name = "presupuesto_innovation_crafters.pdf"

            st.session_state.pdf_data_for_download = pdf_data

            # Preparar datos para Google Sheets
            datos_para_sheets = {
                "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nombre": nombre,
                "Empresa": empresa,
                "CIF/NIF": cif_nif,
                "Teléfono": telefono,
                "Email": email,
                "País": pais,
                "Dirección Fiscal": direccion_fiscal,
                "Dirección de Envío": direccion_envio,
                "Observaciones": observaciones,
                "Materia Prima": materia_prima,
                "Modalidad": modalidad,
                "Unidades Botellas": unidades_botellas,
                "Unidades Extracciones": unidades_extracciones,
                "Coste Botellas": coste_botellas,
                "Coste Extracciones": coste_extracciones,
                "Precio Mano Obra": precio_mano_obra,
                "Coste Total Bolsas": coste_total_bolsas,
                "Total Kg": total_kg,
                "Bolsas (Detalle)": bolsas,
                "Gestión Granel": granel_gestion,
                "Tipo Envío": tipo_envio,
                "Recargo Equivalencia": recargo,
                "IVA Aplicado": iva_aplicado,
                "Total Presupuesto": total
            }

            # Guardar en Google Sheets
            guardar_presupuesto_en_sheets(datos_para_sheets)

            # Enviar correo electrónico
            if enviar_email_con_adjunto(email, pdf_data, file_name, lang["asunto_email"], lang["cuerpo_email_html"], lang["cuerpo_email_plain"]):
                st.session_state.presupuesto_enviado = True
                st.success(lang["exito_email"])
                st.rerun()
            else:
                st.error(lang["error_email"])

