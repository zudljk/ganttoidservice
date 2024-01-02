FROM python

RUN mkdir /app
ADD requirements.txt /app 
ADD app.py /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "gunicorn", "app:app" ]
