FROM python:3

WORKDIR /app

RUN mkdir my_quantified_self

COPY requirements.txt .
COPY my_quantified_self /app/my_quantified_self
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./my_quantified_self/main.py" ]
