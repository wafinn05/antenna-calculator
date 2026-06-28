# Gunakan base image Python yang ringan
FROM python:3.11-slim

# Set environment variables untuk mencegah Python menulis file .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory di dalam container
WORKDIR /app

# Copy file requirements terlebih dahulu untuk memanfaatkan cache layer Docker
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode backend ke dalam container
COPY . .

# Hugging Face Spaces secara default menggunakan port 7860
EXPOSE 7860

# Jalankan aplikasi FastAPI menggunakan Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
