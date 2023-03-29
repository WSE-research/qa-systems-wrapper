
# TODO make it work
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt; exit 0
RUN pip install uvicorn[standard]

COPY main.py ./
COPY certs certs

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host=0.0.0.0", "--port=8080"]      
