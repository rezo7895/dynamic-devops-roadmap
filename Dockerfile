FROM python:3.13-slim
WORKDIR /app
COPY ./app.py ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV APP_VERSION=v0.0.2

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]