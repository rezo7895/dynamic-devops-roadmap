FROM python:3.13.0
WORKDIR /app
COPY . .
CMD [ "python","app.py" ]