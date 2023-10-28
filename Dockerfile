# Dockerfile

# set base image
FROM python:3.10-alpine

LABEL org.opencontainers.image.source="https://github.com/wichmann/evreg"
ENV EVREG_IS_CONTAINER=1
WORKDIR /app

# setup Python libs
COPY requirements.txt /app
RUN pip install -r requirements.txt

# copy app to container
ADD static /app/static
ADD templates /app/templates
COPY app.py /app
COPY config.py /app
COPY mail.py /app
COPY model.py /app

# set command
ENTRYPOINT [ "python" ]
CMD ["app.py" ]
