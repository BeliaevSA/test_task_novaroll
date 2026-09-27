"""
Скрипт наполнения БД начальными данными: 2 менеджера и 5 звонков.

По условию задачи:
    - у менеджера Иванова 3 звонка, два из них повторные в одну и ту же
      организацию ("ООО Ромашка"), третий - в другую организацию;
    - у менеджера Петрова 2 звонка в разные организации.
Таблицы call_summaries и examples на этом этапе не заполняются.

Запуск локально:
    cd backend
    python -m app.seed_data

Запуск в контейнере:
    docker compose exec backend python -m app.seed_data
"""

from datetime import datetime

from app.database import Base, engine, SessionLocal
from app import models
from app.crud.managers_crud import create_manager, get_managers
from app.crud.calls_crud import create_call, get_calls
from app.schemas import ManagerCreate, CallCreate


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Если данные уже есть - повторно не заполняем
        if get_managers(db) or get_calls(db):
            print("В БД уже есть данные, заполнение пропущено.")
            return

        # ---- Менеджеры ----
        ivanov = create_manager(db, ManagerCreate(first_name="Иван", last_name="Иванов"))
        petrov = create_manager(db, ManagerCreate(first_name="Петр", last_name="Петров"))

        # ---- Звонки ----
        calls = [
            # Иванов: 2 повторных звонка в одну организацию
            CallCreate(
                call_datetime=datetime(2026, 9, 10, 10, 0),
                organization="ООО Ромашка",
                duration_seconds=725,
                manager_id=ivanov.id,
                call_link="files/2026_09_10_10_00_ivanov.docx",
            ),
            CallCreate(
                call_datetime=datetime(2026, 9, 15, 14, 30),
                organization="ООО Ромашка",
                duration_seconds=649,
                manager_id=ivanov.id,
                call_link="files/2026_09_15_14_30_ivanov.docx",
            ),
            # Иванов: звонок в другую организацию
            CallCreate(
                call_datetime=datetime(2026, 9, 20, 11, 15),
                organization="ЗАО Вектор",
                duration_seconds=525,
                manager_id=ivanov.id,
                call_link="files/2026_09_20_11_15_ivanov.docx",
            ),
            # Петров: 2 звонка в разные организации
            CallCreate(
                call_datetime=datetime(2026, 9, 12, 9, 45),
                organization="ООО Технологии",
                duration_seconds=581,
                manager_id=petrov.id,
                call_link="files/2026_09_12_09_45_petrov.docx",
            ),
            CallCreate(
                call_datetime=datetime(2026, 9, 18, 16, 0),
                organization="ИП Сидоров",
                duration_seconds=457,
                manager_id=petrov.id,
                call_link="files/2026_09_18_16_00_petrov.docx",
            ),
        ]

        for call in calls:
            create_call(db, call)

        print("Данные успешно добавлены: 2 менеджера, 5 звонков.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
