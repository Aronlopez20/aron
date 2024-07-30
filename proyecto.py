import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuración de Streamlit
st.title('Predicción de Obesidad')

# Ruta al archivo CSV en la carpeta de descargas
# Ajusta esta ruta según el sistema operativo y el nombre del archivo
ruta_archivo = os.path.expanduser('~/Descargas/archive/obesity_data.csv')  # Para sistemas basados en Unix (Linux/Mac)
# ruta_archivo = os.path.join(os.path.expanduser('~'), 'Downloads', 'archivo.csv')  # Alternativa para Windows

if os.path.isfile(ruta_archivo):
    try:
        # Cargar los datos
        data = pd.read_csv(ruta_archivo)
        
        # Mostrar las primeras filas del dataset
        st.write("Primeras filas del dataset:", data.head())

        # Seleccionar el número de filas para trabajar
        num_filas = st.slider('Selecciona el número de filas para analizar', 
                              min_value=100, max_value=len(data), value=min(1000, len(data)), step=100)
        data = data.head(num_filas)

        # Verificar columnas necesarias
        required_columns = [
            'Age', 'Gender', 'Height', 'Weight', 'BMI', 
            'PhysicalActivityLevel', 'ObesityCategory'
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            st.error(f"El archivo CSV no contiene las siguientes columnas requeridas: {', '.join(missing_columns)}")
        else:
            # Función para graficar y mostrar gráficos en Streamlit
            def plot_and_show(data, x, y=None, title='', xlabel='', ylabel='', plot_type='bar', color='blue', regplot=False):
                plt.figure(figsize=(10, 6))
                if plot_type == 'bar':
                    sns.countplot(x=x, data=data, color=color)
                elif plot_type == 'scatter':
                    if regplot:
                        sns.regplot(x=x, y=y, data=data, scatter_kws={'color':'blue'}, line_kws={'color':'red'})
                    else:
                        sns.scatterplot(x=x, y=y, data=data, color=color)
                elif plot_type == 'hist':
                    sns.histplot(data[x], bins=30, kde=True, color=color)
                elif plot_type == 'pie':
                    counts = data[x].value_counts()
                    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
                    plt.axis('equal')
                plt.title(title)
                if plot_type != 'pie':
                    plt.xlabel(xlabel)
                    plt.ylabel(ylabel)
                    plt.xticks(rotation=45)
                    plt.grid(True)
                st.pyplot(plt.gcf())
                plt.close()

            # Gráficos
            plot_and_show(data, 'Age', title='Distribución de Edades', xlabel='Edad', ylabel='Frecuencia', plot_type='hist', color='teal')
            plot_and_show(data, 'Gender', title='Distribución de Género', plot_type='pie')
            plot_and_show(data, 'Height', 'Weight', 'Relación entre Altura y Peso', 'Altura', 'Peso', 'scatter', 'green', regplot=True)
            plot_and_show(data, 'BMI', title='Distribución de BMI', xlabel='BMI', ylabel='Frecuencia', plot_type='hist', color='orange')
            plot_and_show(data, 'PhysicalActivityLevel', title='Distribución de Nivel de Actividad Física', plot_type='pie')
            plot_and_show(data, 'ObesityCategory', title='Distribución de Categoría de Obesidad', plot_type='pie')

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.error(f"No se encontró el archivo en la ruta especificada: {ruta_archivo}")