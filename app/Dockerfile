FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# COPY app /app/app
# COPY run.py /app/
# COPY app/init.sh /app/
COPY app /app/
RUN chmod +x /app/init.sh && /app/init.sh

EXPOSE 5000

ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

CMD ["flask", "run"]
# CMD ["python", "run.py"]
