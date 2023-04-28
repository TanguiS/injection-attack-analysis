FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
ENV VERSION=${SET_VERSION:-NOT_DEFINED}
ENV ROOT_PATH=/
EXPOSE 80
COPY ./app app
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get -y install libgl1 libglib2.0-0 -y

RUN apt-get update \
  && apt-get -y install tesseract-ocr \ 
  && apt-get -y install ffmpeg libsm6 libxext6 # required for opencv

RUN apt-get -y install poppler-utils
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]
