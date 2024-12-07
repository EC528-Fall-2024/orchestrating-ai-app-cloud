FROM python:3.9-slim

WORKDIR /src

COPY requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/

CMD ["python", "main.py"]
