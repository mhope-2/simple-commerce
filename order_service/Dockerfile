FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy files
ADD . /app/

EXPOSE 8083

RUN export PYTHONPATH=.

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]