FROM python:3.13-rc-bookworm

WORKDIR /app
COPY . .

RUN python -m pip install -r requirements.txt
CMD ["python", "RimTranslate.py", "-p", "po/", "-o", "output/"]
