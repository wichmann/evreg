# Dockerfile for evreg

# set base image
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="evreg"
LABEL org.opencontainers.image.description="A simple web app to register for a school event and validate mail addresses of the student and the trainer."
LABEL org.opencontainers.image.version="1.1.0"
LABEL org.opencontainers.image.authors="wichmann@bbs-os-brinkstr.de"
LABEL org.opencontainers.image.licenses="MIT License"
LABEL org.opencontainers.image.documentation="https://github.com/wichmann/evreg/blob/master/README.md"
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
