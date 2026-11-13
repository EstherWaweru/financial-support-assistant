FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

ADD . /app

RUN python -m pip install --upgrade pip

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ ${INSTALL_DEV} == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"



ENV PYTHONPATH=/app
ENV C_FORCE_ROOT=1

ENTRYPOINT ["bash", "-c", "uvicorn main:application --host 0.0.0.0"]
