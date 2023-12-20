# Build stage
FROM python:3.9-slim as build

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim as runtime

WORKDIR /app

COPY --from=build /root/.local /root/.local
COPY --from=build /app /app

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH
ENV FLASK_ENV=production

EXPOSE 5003

CMD ["python", "/app/main.py"]
