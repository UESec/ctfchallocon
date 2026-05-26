FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        netcat-openbsd \
        procps \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash cakeoperator

WORKDIR /opt/orange-plant

COPY requirements.txt /opt/orange-plant/requirements.txt
RUN pip install --no-cache-dir -r /opt/orange-plant/requirements.txt

COPY app /opt/orange-plant/app
COPY classified /opt/orange-plant/classified

RUN chown -R cakeoperator:cakeoperator /opt/orange-plant \
    && chmod 755 /opt/orange-plant \
    && chmod 755 /opt/orange-plant/classified \
    && chmod 444 /opt/orange-plant/classified/orange_cake_enrichment_formula.flag

USER cakeoperator

EXPOSE 80

CMD ["python3", "/opt/orange-plant/app/app.py"]
