FROM python

RUN mkdir /app
ADD requirements.txt /app 
ADD app.py /app

WORKDIR /app

EXPOSE 8000

RUN pip install -r requirements.txt

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:app" ]
