import streamlit as st
import pandas as pd

# Cargar el dataset
data_path = '/home/lopez/Descargas/archive/Heart_Disease_Prediction.csv'  # Asegúrate de que esta ruta sea correcta
try:
    data = pd.read_csv(data_path)
except FileNotFoundError:
    st.error("El archivo no se encontró. Verifica la ruta del archivo.")
    st.stop()

# Título de la aplicación
st.title('Análisis de Datos con Streamlit')

# Mostrar el dataframe
st.write(data)

# Mostrar algunas estadísticas básicas
st.write(data.describe())

# Mostrar un gráfico
if 'columna' in data.columns:
    st.line_chart(data['columna'])  # Cambia 'columna' por el nombre de la columna que deseas graficar
else:
    st.warning("La columna especificada no existe en el dataset.")

if __name__ == '__main__':
    st.run()
