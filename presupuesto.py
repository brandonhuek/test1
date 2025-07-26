
import streamlit as st

st.set_page_config(page_title="Presupuesto Innovation Crafters", layout="centered")
st.title("Presupuesto personalizado Innovation Crafters")

# Simulación del formulario
nombre = st.text_input("Nombre")
email = st.text_input("Email")
modalidad = st.selectbox("Modalidad", ["Standard", "Premium", "Platino"])

if st.button("📩 Enviar y Descargar Presupuesto"):
    # Aquí iría la lógica de PDF y envío por correo

    # Redirigir a la página de confirmación
    st.experimental_set_query_params(pagina="confirmacion")
    st.switch_page("confirmacion.py")
