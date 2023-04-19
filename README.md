# Qa Systems Wrapper

## Current Location

http://141.57.8.18:40199/docs

## How to run (development)

```bash
python main.py
```

or

```bash
exec uvicorn main:app --reload --host 0.0.0.0 --port=41021 --ssl-keyfile=/etc/ssl/webengineering.ins.hs-anhalt.de/nginx/webengineering.ins.hs-anhalt.de.key --ssl-certfile=/etc/ssl/webengineering.ins.hs-anhalt.de/nginx/webengineering.ins.hs-anhalt.de.cert
```