FROM python:3.11-slim

RUN pip install -U pip pip-tools

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY brit/ ./brit/

RUN pip-sync

ENV DATABASE_FILE shopping-lists.db
ENV DEBUG ""

EXPOSE 8000

#ENTRYPOINT ["uvicorn", "brit:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
ENTRYPOINT ["uvicorn", "brit:app", "--host", "0.0.0.0", "--port", "8000"]
