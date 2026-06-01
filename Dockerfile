FROM python:3.10-slim

WORKDIR /app

# system deps (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PORT=8501
EXPOSE 8501

CMD ["sh","-c","streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]
