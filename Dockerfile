FROM python:latest

COPY . /app
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt
RUN chmod +x /app/server_start.dev.sh /app/server_start.prod.sh

EXPOSE 8000
WORKDIR /app

CMD ["/app/server_start.prod.sh"]