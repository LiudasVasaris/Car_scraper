FROM python:3.8

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY app/ /app

WORKDIR app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# uvicorn app.main:app --host 0.0.0.0 --port 80
