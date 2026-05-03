FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install tgcf==1.0.9
COPY . .
CMD ["python", "main.py"]
