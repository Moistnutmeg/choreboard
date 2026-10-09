FROM python:3.11-slim
WORKDIR /app
RUN pip install flask --no-cache-dir
COPY app.py .
COPY templates/ templates/
COPY static/ static/
VOLUME ["/data"]
EXPOSE 8090
CMD ["python", "app.py"]
