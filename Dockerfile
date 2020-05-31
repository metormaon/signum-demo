FROM ubuntu:16.04
FROM python:3.7

ADD venv/lib/python3.7/site-packages /package-cache
ADD requirements.txt /requirements.txt

RUN pip install -r requirements.txt

ADD static /static
ADD templates /templates
ADD resources /resources
ADD *.py /

EXPOSE 5000

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

