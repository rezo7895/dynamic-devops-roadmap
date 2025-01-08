FROM python:3.13-slim
RUN groupadd -g 1000 hiveboxgroup && \
    useradd -m -u 1000 -g hiveboxgroup hiveboxuser
WORKDIR /app
COPY ./app.py ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
USER hiveboxuser
EXPOSE 5000
CMD [ "python","app.py" ]