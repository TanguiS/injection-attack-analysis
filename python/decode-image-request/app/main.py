import os
from email.mime.application import MIMEApplication

from fastapi import FastAPI, Depends
from app.routers import reports, consents, html
# from starlette_oauth2_api import AuthenticateMiddleware
from fastapi.security import HTTPBearer
from app.core.config import settings
import uvicorn
import base64
from app.schemas import schemas
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, status
from fastapi.responses import FileResponse
from app.routers.reports import get_db, save_pdf
from app.crud import crud_report, crud_user
from weasyprint import HTML
from PIL import Image, ExifTags
from images_decode.decoder import decode_image, decode_list_of_image

from app.routers.reports import send_report_to_email, create_pdf_file

app = FastAPI(
    title=settings.app_name,
    description="This service is used to store report data, and generate reports in different formats e.g PDF and XML",
    version=settings.version,
)


@app.get("/")
def information():
    return {
        "title": settings.app_name,
        "description": "API for saving reports, documentation: /redoc",
        "version": settings.version,
    }


@app.post("/imageToDecode", status_code=status.HTTP_200_OK)
def req_image_to_decode(rep: schemas.ImageToDecode):
    try:
        decode_image(rep)
    except:
        # return {"400": "error to parse the data from client"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="error occurred when parsing the data from client")
    return {status.HTTP_200_OK: "OK, sent report"}


@app.post("/ListOfImageToDecode", status_code=status.HTTP_200_OK)
def req_list_of_image_to_decode(rep: schemas.ListOfImageToDecode):
    try:
        decode_list_of_image(rep)
    except:
        # return {"400": "error to parse the data from client"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="error occurred when parsing the data from client")
    return {status.HTTP_200_OK: "OK, sent report"}


if __name__ == '__main__':
    # credentials = ("report@msmobai.onmicrosoft.com", "Wat40369")
    #
    # account = Account(credentials)
    # m = account.new_message()
    # m.to.add('gl@mobai.bio')
    # m.subject = 'Testing!'
    # m.body = "George Best quote: I've stopped drinking, but only while I'm asleep."
    # m.send()
    # testMobaiemail()
    # username = "vostro0120@126.com"
    # passwd = "red1983*"
    # recv = "gl@mobai.bio"
    # title = "test report"
    # content = "this is test report, please find in the attachment"
    # file = "./reports/e5b14e94-2442-4fcb-abbf-aeabe32c9f2f.pdf"
    # send_mail(username, passwd, recv, title, content, file=file)

    # sendattach("Test Email", './reports/temp.pdf', "testname.pdf")

    # testing_send_email()
    # strImageFilePath = "/Users/guoqiangli/workspace/image.png"
    # with open(strImageFilePath, "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read())

    uvicorn.run(app, host="localhost", port=8080)
