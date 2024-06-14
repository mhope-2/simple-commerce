FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy files
ADD . /app/

EXPOSE 8082

RUN export PYTHONPATH=.

# Startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083", "--reload"]