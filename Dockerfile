# Usamos una imagen base ligera de Python
FROM python:3.9-slim

# Directorio de trabajo
WORKDIR /app

# Copiamos los requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (scripts y PDFs de prueba)
COPY . .

# Comando por defecto (esto se sobreescribirá en el CronJob de K8s, 
# pero lo dejamos listo para pruebas locales)
CMD ["python", "compare_pdfs.py", "DocumentoA_1.pdf", "DocumentoA2.pdf"]