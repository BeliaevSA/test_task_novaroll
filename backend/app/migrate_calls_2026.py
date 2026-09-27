
from datetime import datetime

from app.database import SessionLocal
from app import models


def migrate_calls() -> None:
    db = SessionLocal()

    # Старые данные -> новые данные
    migrations = [
        {
            "old_link": "files/2024_09_10_10_00_ivanov.docx",
            "new_link": "files/2026_09_10_10_00_ivanov.docx",
            "new_datetime": datetime(2026, 9, 10, 10, 0),
            "new_duration": 725,
        },
        {
            "old_link": "files/2024_09_15_14_30_ivanov.docx",
            "new_link": "files/2026_09_15_14_30_ivanov.docx",
            "new_datetime": datetime(2026, 9, 15, 14, 30),
            "new_duration": 649,
        },
        {
            "old_link": "files/2024_09_20_11_15_ivanov.docx",
            "new_link": "files/2026_09_20_11_15_ivanov.docx",
            "new_datetime": datetime(2026, 9, 20, 11, 15),
            "new_duration": 525,
        },
        {
            "old_link": "files/2024_09_12_09_45_petrov.docx",
            "new_link": "files/2026_09_12_09_45_petrov.docx",
            "new_datetime": datetime(2026, 9, 12, 9, 45),
            "new_duration": 581,
        },
        {
            "old_link": "files/2024_09_18_16_00_petrov.docx",
            "new_link": "files/2026_09_18_16_00_petrov.docx",
            "new_datetime": datetime(2026, 9, 18, 16, 0),
            "new_duration": 457,
        },
    ]

    try:
        # Сначала проверяем, что найдены все пять старых записей.
        calls_to_update = []

        for item in migrations:
            call = (
                db.query(models.Call)
                .filter(
                    models.Call.call_link == item["old_link"]
                )
                .one_or_none()
            )

            if call is None:
                raise ValueError(
                    "Не найдена запись: "
                    + item["old_link"]
                )

            calls_to_update.append((call, item))

        # Если все записи найдены, обновляем их.
        for call, item in calls_to_update:
            call.call_datetime = item["new_datetime"]
            call.duration_seconds = item["new_duration"]
            call.call_link = item["new_link"]

        db.commit()

        print("Миграция успешно выполнена.")
        print(f"Обновлено звонков: {len(calls_to_update)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    migrate_calls()