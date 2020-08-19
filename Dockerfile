FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY my_quantified_self ./


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./your-daemon-or-script.py" ]
