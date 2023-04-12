FROM python:3.9

RUN mkdir -p /app
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD python app.py