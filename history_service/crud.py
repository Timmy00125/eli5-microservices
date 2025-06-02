from sqlalchemy.orm import Session
import models
import schemas


def create_history_record(
    db: Session, user_id: int, record_data: schemas.HistoryRecordCreate
):
    db_record = models.HistoryRecord(user_id=user_id, data=record_data.concept_details)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_history_records_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
):
    return (
        db.query(models.HistoryRecord)
        .filter(models.HistoryRecord.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
