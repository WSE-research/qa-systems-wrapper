
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install uvicorn[standard]
RUN pip install --force-reinstall httpcore==0.15

COPY main.py ./
COPY routers routers

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8080"]      
