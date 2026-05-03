FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install tgcf==1.1.8
COPY . .
CMD ["python", "main.py"]
