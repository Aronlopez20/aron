import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt

class ETLGUI:
    def __init__(self, master):
        self.master = master
        master.title("Proceso ETL")
        master.geometry("700x500")
        master.configure(bg="#2c3e50")

        # Estilos
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Arial", 12))
        style.configure("TButton", background="#1abc9c", foreground="#ecf0f1", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TProgressbar", troughcolor="#34495e", background="#1abc9c")

        # Configuración del grid
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(5, weight=1)

        # Botón para seleccionar carpeta
        self.folder_button = ttk.Button(master, text="Seleccionar carpeta de datos", command=self.select_folder)
        self.folder_button.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

        # Entrada para rango de columnas
        ttk.Label(master, text="Rango de columnas (ej. A:S):").grid(row=1, column=0, sticky="w", padx=20)
        self.column_range = ttk.Entry(master)
        self.column_range.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
        self.column_range.insert(0, "A:S")  # Valor predeterminado

        # Entrada para fila inicial
        ttk.Label(master, text="Fila inicial:").grid(row=2, column=0, sticky="w", padx=20)
        self.start_row = ttk.Entry(master)
        self.start_row.grid(row=2, column=0, pady=5, padx=20, sticky="ew")
        self.start_row.insert(0, "13")  # Valor predeterminado

        # Botón para iniciar proceso
        self.process_button = ttk.Button(master, text="Iniciar proceso ETL", command=self.start_etl)
        self.process_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        # Barra de progreso
        self.progress = ttk.Progressbar(master, length=400, mode='determinate')
        self.progress.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

        # Área de texto para mostrar resultados
        self.result_text = tk.Text(master, height=10, bg="#34495e", fg="#ecf0f1", font=("Arial", 12))
        self.result_text.grid(row=5, column=0, pady=10, padx=20, sticky="nsew")

        self.folder_path = ""

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.result_text.insert(tk.END, f"Carpeta seleccionada: {self.folder_path}\n")

    def start_etl(self):
        if not self.folder_path:
            self.result_text.insert(tk.END, "Por favor, seleccione una carpeta primero.\n")
            return

        col_range = self.column_range.get()
        start_row = int(self.start_row.get()) if self.start_row.get().isdigit() else 13

        try:
            # Obtener lista de archivos Excel en la carpeta, excluyendo Out.xlsx
            excel_files = [f for f in os.listdir(self.folder_path) if f.endswith('.xlsx') and f != 'Out.xlsx']

            # Inicializar DataFrame final
            final_df = pd.DataFrame()

            # Configurar barra de progreso
            self.progress['value'] = 0
            self.progress['maximum'] = len(excel_files)

            column_names = ['OFICINA', 'CODIGO', 'NOMBRE', 'LINEA', 'GRUPO', 'PNG', 'U', 'VALOR', 'U2', 'VALOR2', 'LV1', 'VALORC', 'LV2', 'COL14', 'COL15', 'COL16', 'ANIO', 'MES', 'DIA']

            for file in excel_files:
                file_path = os.path.join(self.folder_path, file)
                
                # Leer archivo Excel
                df = pd.read_excel(file_path, usecols=col_range, skiprows=start_row-1, header=None, engine='openpyxl')
                
                # Asegurar que tenemos el número correcto de columnas
                if len(df.columns) < len(column_names) - 3:  # -3 porque añadiremos ANIO, MES, DIA después
                    df = df.reindex(columns=range(len(column_names) - 3))
                elif len(df.columns) > len(column_names) - 3:
                    df = df.iloc[:, :(len(column_names) - 3)]
                
                # Extraer año, mes y día del nombre del archivo
                try:
                    date_parts = file.split('.')
                    year, month, day = date_parts[1], date_parts[2], date_parts[3]
                except IndexError:
                    year, month, day = "0000", "00", "00"
                    self.result_text.insert(tk.END, f"Advertencia: No se pudo extraer la fecha del archivo {file}. Se usaron valores predeterminados.\n")
                
                # Añadir columnas de fecha
                df['ANIO'] = year
                df['MES'] = month
                df['DIA'] = day
                
                # Asignar nombres de columnas
                df.columns = column_names
                
                # Concatenar al DataFrame final
                final_df = pd.concat([final_df, df], ignore_index=True)
                
                # Actualizar barra de progreso
                self.progress['value'] += 1
                self.master.update_idletasks()

            # Exportar a Excel
            output_path = os.path.join(self.folder_path, 'Out.xlsx')
            final_df.to_excel(output_path, index=False, engine='openpyxl')

            self.result_text.insert(tk.END, f"Proceso ETL completado. Archivo guardado en: {output_path}\n")
            self.result_text.insert(tk.END, f"Dimensiones del DataFrame final: {final_df.shape}\n")
            self.result_text.insert(tk.END, f"Primeras filas del DataFrame:\n{final_df.head().to_string()}\n")

            # Generar reportes gráficos
            self.generate_reports(final_df)

        except Exception as e:
            self.result_text.insert(tk.END, f"Error durante el proceso ETL: {str(e)}\n")
            messagebox.showerror("Error", f"Se produjo un error durante el proceso ETL: {str(e)}")

    def generate_reports(self, df):
        # Crear una carpeta para los reportes si no existe
        reports_folder = os.path.join(self.folder_path, 'Reportes')
        os.makedirs(reports_folder, exist_ok=True)

        # Gráfico 1: Conteo de registros por oficina
        plt.figure(figsize=(10, 6))
        df['OFICINA'].value_counts().plot(kind='bar', color='#1abc9c')
        plt.title('Conteo de Registros por Oficina')
        plt.xlabel('Oficina')
        plt.ylabel('Cantidad de Registros')
        plt.tight_layout()
        plt.savefig(os.path.join(reports_folder, 'conteo_por_oficina.png'))
        plt.close()

        # Gráfico 2: Distribución de valores
        plt.figure(figsize=(10, 6))
        df['VALOR'].hist(bins=50, color='#e74c3c')
        plt.title('Distribución de Valores')
        plt.xlabel('Valor')
        plt.ylabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(os.path.join(reports_folder, 'distribucion_valores.png'))
        plt.close()

        # Gráfico 3: Evolución temporal de valores (si hay suficientes datos)
        if df['ANIO'].nunique() > 1 or df['MES'].nunique() > 1:
            plt.figure(figsize=(12, 6))
            df.groupby(['ANIO', 'MES'])['VALOR'].mean().plot(kind='line', color='#3498db')
            plt.title('Evolución Temporal de Valores')
            plt.xlabel('Año-Mes')
            plt.ylabel('Valor Promedio')
            plt.tight_layout()
            plt.savefig(os.path.join(reports_folder, 'evolucion_temporal.png'))
            plt.close()

        # Nuevo gráfico 4: Gráfico de torta para distribución por LINEA
        plt.figure(figsize=(10, 8))
        df['LINEA'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#1abc9c', '#e74c3c', '#3498db', '#9b59b6'])
        plt.title('Distribución de Registros por Línea')
        plt.ylabel('')  # Elimina la etiqueta del eje y para mejor visualización
        plt.tight_layout()
        plt.savefig(os.path.join(reports_folder, 'distribucion_por_linea.png'))
        plt.close()

        self.result_text.insert(tk.END, f"Reportes gráficos generados en: {reports_folder}\n")

if __name__ == "__main__":
    root = tk.Tk()
    etl_gui = ETLGUI(root)
    root.mainloop()