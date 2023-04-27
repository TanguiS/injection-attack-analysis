import base64, uuid
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas


def create_report(db: Session, report: schemas.ReportCreate, user_id: uuid.UUID, org_id: uuid.UUID):
    report.passport_photo = base64.b64decode(report.passport_photo)
    db_report = models.Report(
        **report.dict(exclude = {"photo_comparisons"}),
        created_by=user_id,
        organization_id=org_id
    )

    db.add(db_report)
    db.flush() # so report ID can be retrieved

    db_report.pdf = f"report-{db_report.id}.pdf"
    
    save_photo_comparisons(db, db_report.id, report.photo_comparisons)
        
    db.commit()

    return db_report


def get_report(db: Session, id: uuid.UUID, org_id: uuid.UUID):
    report: schemas.Report = db.query(models.Report).filter(
        models.Report.id == id,
        models.Report.organization_id == org_id
    ).first()

    if report:
        report.passport_photo = base64.b64encode(report.passport_photo).decode("utf-8")

        if len(report.photo_comparisons) > 0:
            for photo_compare in report.photo_comparisons:
                photo_compare.photo_one = base64.b64encode(photo_compare.photo_one).decode("utf-8")
                photo_compare.photo_two = base64.b64encode(photo_compare.photo_two).decode("utf-8")

    return report


def get_all_reports(db: Session, org_id: uuid.UUID, user_id: uuid.UUID = None):
    if user_id is not None:
        return db.query(models.Report.id).filter(
            models.Report.created_by == user_id,
            models.Report.organization_id == org_id
        ).all()
    
    return db.query(models.Report.id).filter(models.Report.organization_id == org_id).all()


def update_report(db: Session, id: uuid.UUID, report: schemas.ReportCreate, user_id: uuid.UUID, org_id: uuid.UUID):
    update_data = report.dict(exclude={"photo_comparisons", "passport_photo"})
    update_data['created_by'] = user_id
    update_data['passport_photo'] = base64.b64decode(report.passport_photo)

    count = db.query(models.Report).filter(
        models.Report.id == id,
        models.Report.organization_id == org_id
    ).update(update_data)
    
    db.flush()

    if count > 0:
        db.query(models.PhotoCompare).filter(models.PhotoCompare.report_id == id).delete()
        save_photo_comparisons(db, id, report.photo_comparisons)
    
    db.commit()

    return count


def delete_report(db: Session, id: uuid.UUID, org_id: uuid.UUID):
    count = db.query(models.Report).filter(
        models.Report.id == id,
        models.Report.organization_id == org_id
    ).delete()

    db.commit()

    return count


def delete_all_reports(db: Session, org_id: uuid.UUID):
    reports = get_all_reports(db, org_id)

    db.query(models.Report).filter(models.Report.organization_id == org_id).delete()    
    db.commit()

    return reports


def save_photo_comparisons(db: Session, id: uuid.UUID, photo_comparisons):
    if len(photo_comparisons) > 0:
        for photo_compare in photo_comparisons:
            db_photo_compare = models.PhotoCompare(
                report_id = id,
                photo_one = base64.b64decode(photo_compare.photo_one),
                photo_two = base64.b64decode(photo_compare.photo_two),
                score = photo_compare.score
            )

            db.add(db_photo_compare)

        db.flush()