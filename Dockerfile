FROM python:3.9-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /opt/moneynote
RUN mkdir -p /opt/moneynote

COPY backend /opt/moneynote
COPY requirements.txt /opt/moneynote
COPY docker-entrypoint.sh /opt/moneynote
COPY .env /opt/moneynote/

RUN pip install -r requirements.txt

RUN chmod +x /opt/moneynote/docker-entrypoint.sh

ENTRYPOINT ["/opt/moneynote/docker-entrypoint.sh"]