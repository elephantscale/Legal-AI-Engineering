# Lab 06 — the processing container.
#
# Three things make this image defensible rather than merely working:
#
#   1. The base image is referenced by DIGEST, not by tag. `python:3.12-slim` is a moving
#      target; someone else building this Dockerfile next year gets a different image and
#      your reproducibility claim is gone. A digest is a pin.
#   2. Dependencies are version-pinned in requirements-lab.txt. For a real matter, go
#      further: `pip install --require-hashes`.
#   3. It runs as a non-root user and owns no credentials. There is nothing in this
#      container to steal and nowhere for it to call.
#
# Replace the digest below with the one you actually pulled:
#     docker pull python:3.12-slim
#     docker inspect --format='{{index .RepoDigests 0}}' python:3.12-slim
#
FROM python:3.12-slim@sha256:REPLACE_WITH_THE_DIGEST_YOU_PULLED AS base

# System packages for the real extraction path. Each one is here for a reason:
#   tesseract-ocr        local OCR — the whole point: scans never leave the machine
#   poppler-utils        pdftotext/pdfimages for the PDF path
#   libmagic1            content-type sniffing (do not trust file extensions)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      tesseract-ocr tesseract-ocr-eng poppler-utils libmagic1 \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements-lab.txt /app/
RUN pip install --no-cache-dir -r requirements-lab.txt

# The pipeline code. Copy the labs tree, not the corpus: case data is mounted at run
# time, never baked into an image. An image containing case data is a copy of the
# evidence that you will forget you made.
COPY common/        /app/common/
COPY 01-Ingestion/  /app/01-Ingestion/
COPY 02-Search/     /app/02-Search/
COPY 03-Legal-RAG-Citations/ /app/03-Legal-RAG-Citations/
COPY 04-Local-Model-Egress-Proof/ /app/04-Local-Model-Egress-Proof/
COPY 05-Defensible-Review/        /app/05-Defensible-Review/
COPY 06-Score-and-Package/        /app/06-Score-and-Package/

# Non-root. The corpus mount is read-only; /work is the only writable path.
RUN useradd --create-home --uid 10001 legal \
 && mkdir -p /work && chown legal:legal /work
USER legal

ENV LEGAL_AI_BASE_URL=http://llm:11434/v1 \
    LEGAL_AI_MODEL=qwen3:8b \
    LEGAL_AI_EMBED=nomic-embed-text \
    LEGAL_AI_EGRESS=deny-lan

WORKDIR /app/06-Score-and-Package
ENTRYPOINT ["python3", "run_matter.py"]
CMD ["--corpus", "/corpus", "--work", "/work", "--resume"]
