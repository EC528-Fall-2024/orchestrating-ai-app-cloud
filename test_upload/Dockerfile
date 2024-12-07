FROM python:3.9-slim
WORKDIR /cynthus-src
COPY requirements.txt /cynthus-src/
RUN pip install -r requirements.txt
COPY . /cynthus-src/
CMD ["python", "main.py"]
