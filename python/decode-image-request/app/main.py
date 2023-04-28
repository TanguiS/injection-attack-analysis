# from starlette_oauth2_api import AuthenticateMiddleware
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException, status

from app.images_decode.decoder import decode_image, decode_list_of_image
from app.schemas import schemas

app = FastAPI(
    title="Injection attack analysis",
    description="This service is used to store report data, and generate reports in different formats e.g PDF and XML",
    version="v1.0",
)


@app.get("/")
def information():
    return {
        "title": "Injection attack analysis",
        "description": "API for saving reports, documentation: /redoc",
        "version": "v1.0",
    }


@app.post("/imageToDecode", status_code=status.HTTP_200_OK)
def req_image_to_decode(rep: schemas.ImageToDecode):
    try:
        decode_image(rep)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="error occurred when parsing the data from client")
    return {status.HTTP_200_OK: "OK, sent report"}


@app.post("/ListOfImageToDecode", status_code=status.HTTP_200_OK)
def req_list_of_image_to_decode(rep: schemas.ListOfImageToDecode):
    try:
        decode_list_of_image(rep)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="error occurred when parsing the data from client")
    return {status.HTTP_200_OK: "OK, sent report"}


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8080)
