import socket
import uuid, os
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.core.database import SessionLocal
from app.schemas import schemas
from app.crud import crud_report, crud_user
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import uuid

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def root():
    return {"msg": "Welcome to the Mobai passport service"}



@router.get("/", response_model=schemas.ReportResponseList)
async def get_all_reports(request: Request, user_id: Optional[uuid.UUID] = None, db: Session = Depends(get_db)):
    db_reports = crud_report.get_all_reports(db, request.scope['oauth2-claims']['tid'], user_id)

    if not db_reports:
        raise HTTPException(status_code=404, detail="Could not find any reports related to the organization or user")

    return {"reports": db_reports}


@router.post("/", response_model=schemas.ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(report: schemas.ReportCreate, request: Request, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user_id = request.scope['oauth2-claims']['oid']
    org_id = request.scope['oauth2-claims']['tid']
    name = request.scope['oauth2-claims']['name']

    user = {
        "id": user_id,
        "organization_id": org_id,
        "name": name
    }

    db_org = crud_user.create_organization(db, org_id)
    db_user = crud_user.create_user(db, user)

    temp = crud_report.create_report(db, report, db_user.id, db_org.id)
    rep = crud_report.get_report(db, temp.id, org_id)

    bg_tasks.add_task(save_pdf, rep) # continue, but save pdf in the background

    return {"id": rep.id}


@router.get("/{id}", response_model=schemas.Report)
async def get_report(request: Request, id: uuid.UUID, db: Session = Depends(get_db)):
    db_report = crud_report.get_report(db, id, request.scope['oauth2-claims']['tid'])
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return db_report


@router.get("/{id}/pdf", response_class=FileResponse, responses={
    200: {
        "content": {"application/pdf": {}}, 
        "description": "Returns report as PDF"
        }
    },
)
async def get_report_pdf(id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    db_report = crud_report.get_report(db, id, request.scope['oauth2-claims']['tid'])
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if not os.path.exists(f'/app/reports/{db_report.pdf}'):
        save_pdf(db_report)

    return FileResponse(f'/app/reports/{db_report.pdf}', media_type="application/pdf")


@router.put('/{id}')
def update_report(id: uuid.UUID, report: schemas.ReportCreate, request: Request, db: Session = Depends(get_db)) -> schemas.Report:
    user_id = request.scope['oauth2-claims']['oid']
    org_id = request.scope['oauth2-claims']['tid']

    count = crud_report.update_report(db, id, report, user_id, org_id)

    if count > 0:
        save_pdf(crud_report.get_report(db, id, org_id))
        return {"description": "OK"}

    return {"description": "Nothing updated"}


@router.delete("/")
def delete_all_reports(request: Request, db: Session = Depends(get_db)):
    report = crud_report.delete_all_reports(db, request.scope['oauth2-claims']['tid'])
    # @todo delete all pdfs also?

    if not report:
        raise HTTPException(status_code=404, detail="Could not find any reports to delete")
    
    return report


@router.delete("/{id}")
def delete_report(request: Request, id: uuid.UUID, db: Session = Depends(get_db)):
    report = crud_report.delete_report(db, id, request.scope['oauth2-claims']['tid'])

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


def save_pdf(rep: schemas.Report):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template('app/templates/report.html')
    html_out = template.render(report=rep, logo='app/templates/logo.png')

    HTML(string=html_out, base_url='.').write_pdf(f'/app/reports/{rep.pdf}', stylesheets=['app/templates/style.css'])


# def send_report_to_email(rep: schemas.ReportContent, report_Path):
#
#     user_name = rep.first_name + " " + rep.last_name
#     email_subject = "Report for " + user_name
#     attachment_filename = user_name.replace(" ", "_") + "_report.pdf"
#     receipt_email_address = rep.receiver_email_address
#     sender_email_address = "mobai.bio@icloud.com"
#     sender_email_passcode = str(os.environ.get("EMAIL_PASSPORD", "mobai.as2019"))
#     sender_email_passcode = 'ihtq-lfhv-qduw-lqbn'
#     print(sender_email_passcode)
#     msg = MIMEMultipart()
#     msg['Subject'] = email_subject
#     msg['From'] = sender_email_address   ## seems this line is required!
#     mail_content = '''Hei,
#         Kindly find the report file in the attachment.
#         Best regards,
#         Mobai Team.
#     '''
#
#
#     msg.attach(MIMEText(mail_content, 'plain'))
#     mimebase_instance = MIMEBase('application', "octet-stream")
#     mimebase_instance.set_payload(open(report_Path, 'rb').read())
#     encoders.encode_base64(mimebase_instance)
#     mimebase_instance.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
#     msg.attach(mimebase_instance)
#     email_session = smtplib.SMTP('smtp.mail.me.com', 587)
#     email_session.ehlo()
#     email_session.starttls()
#     email_session.login(sender_email_address, sender_email_passcode)
#     email_session.sendmail(sender_email_address, receipt_email_address, msg.as_string())
#     email_session.quit()
#     ##delete report file
#     if os.path.exists(report_Path):
#         os.remove(report_Path)


def send_report_to_email(rep: schemas.ReportContent, report_Path, email_session, sender_email_address):
    user_name = rep.first_name + " " + rep.last_name
    email_subject = "Report for " + user_name
    attachment_filename = user_name.replace(" ", "_") + "_report.pdf"
    receipt_email_address = rep.receiver_email_address
    msg = MIMEMultipart()
    msg['Subject'] = email_subject
    msg['From'] = sender_email_address   ## seems this line is required for icloud.com smtp!
    mail_content = '''Hei,
        Kindly find the report file in the attachment.
        Best regards,
        Mobai Team.
    '''
    msg.attach(MIMEText(mail_content, 'plain'))
    mimebase_instance = MIMEBase('application', "octet-stream")
    mimebase_instance.set_payload(open(report_Path, 'rb').read())
    if os.path.exists(report_Path):
        print("pdf file exists")
    else:
        print("pdf file doesnot exist.")
    encoders.encode_base64(mimebase_instance)
    mimebase_instance.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
    msg.attach(mimebase_instance)
    print("before sending email.")
    try:
        email_session.sendmail(sender_email_address, receipt_email_address, msg.as_string())
    except socket.error as e:
        print("socket error: not able to connect to email server")
    except:
        print("unknown error")
    finally:
        print("not able to send email, error")
    print("after sending email")
    ##delete report file
    if os.path.exists(report_Path):
        os.remove(report_Path)



def create_pdf_file(rep: schemas.ReportContent):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template('./templates/report_nordea.html')
    html_out = template.render(report=rep, logo='./templates/logo.png')
    if not os.path.exists("./reports/"):
        os.makedirs("./reports/")
    randomFileName = str(uuid.uuid4()) + ".pdf"
    HTML(string=html_out, base_url='.').write_pdf(f'./reports/' + randomFileName, stylesheets=['./templates/style.css'])
    return randomFileName
