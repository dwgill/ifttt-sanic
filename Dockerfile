FROM python:3.6
MAINTAINER Daniel Dgill <dwgill@outlook.com>
COPY . /app
WORKDIR /app
RUN pip install -r py_deps
EXPOSE 80
ENV APP_PORT 80
ENV APP_WORKERS 1
CMD python -m sanic app.app \
    --host=0.0.0.0 \
    --workers=${APP_WORKERS} \
    --port=${APP_PORT}
