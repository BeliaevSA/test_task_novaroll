# Сводка по звонкам

Проект для хранения и обработки сводок телефонных звонков менеджеров.

## Стек

- **Frontend**: React (Vite, без TypeScript)
- **Backend**: Python (FastAPI)
- **DB**: SQLite (через SQLAlchemy ORM)
- **AI-анализ звонков**: GenAPI (модель gemini-3-5-flash-lite)
- **Деплой**: Docker Compose (VPS)

## Структура проекта

```
call-summary-project/
├── docker-compose.yml
├── frontend/                       # React + Vite
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   │   └── favicon.svg
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       ├── api/
│       │   └── client.js           # обёртка над fetch, все обращения к /api/*
│       ├── utils/
│       │   └── format.js           # форматирование дат/длительности/ФИО
│       ├── components/
│       │   ├── Sidebar.jsx         # сворачиваемый сайдбар
│       │   ├── Modal.jsx           # базовая компактная модалка
│       │   ├── UploadCallModal.jsx # "Загрузить звонок" — заглушка "в разработке"
│       │   ├── DateRangeFilter.jsx # даты от/по (нативный календарь)
│       │   ├── ManagerMultiSelect.jsx  # мультиселект менеджеров с чекбоксами
│       │   ├── CallsTable.jsx      # таблица результатов
│       │   └── SummaryModal.jsx    # полноэкранная модалка сводки звонка
│       └── pages/
│           └── CallSummaryPage.jsx # страница "Сводка по звонкам"
├── backend/                        # FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env                        # GEN_API_KEY (не коммитить)
│   └── app/
│       ├── main.py                 # точка входа, подключение роутов, CORS
│       ├── config.py                # чтение .env (GEN_API_KEY)
│       ├── database.py             # подключение к SQLite
│       ├── models.py               # ORM-модели всех таблиц
│       ├── schemas.py              # Pydantic-схемы (CRUD + анализ GenAPI)
│       ├── init_db.py              # создание таблиц
│       ├── seed_data.py            # наполнение тестовыми данными
│       ├── crud/
│       │   ├── managers_crud.py
│       │   ├── calls_crud.py       # + get_calls_filtered (фильтр по датам/менеджерам)
│       │   ├── summaries_crud.py
│       │   └── examples_crud.py
│       ├── services/
│       │   ├── genapi_client.py    # запрос к GenAPI (gemini-3-5-flash-lite)
│       │   └── docx_export.py      # генерация оформленного .docx со сводкой
│       └── api/
│           ├── managers.py         # GET /managers
│           ├── calls.py            # GET /calls, /calls/{id}/recording,
│           │                       #     /calls/{id}/summary, /calls/{id}/summary/export-docx
│           └── call_summary.py     # POST /calls/{id}/summary/upload-docx (анализ через GenAPI)
├── db/
│   └── calls.db                    # файл базы данных SQLite
└── files/                          # файлы записей звонков (.docx)
    ├── 2026_09_10_10_00_ivanov.docx
    ├── 2026_09_15_14_30_ivanov.docx
    ├── 2026_09_20_11_15_ivanov.docx
    ├── 2026_09_12_09_45_petrov.docx
    └── 2026_09_18_16_00_petrov.docx
```

## Модель данных

### managers (Менеджеры)
| Поле | Тип | Описание |
|---|---|---|
| id | int, PK | идентификатор |
| first_name | str | имя |
| last_name | str | фамилия |

### calls (Звонки)
| Поле | Тип | Описание |
|---|---|---|
| id | int, PK | идентификатор |
| call_datetime | datetime | дата и время звонка (часы, минуты) |
| organization | str | организация |
| duration_seconds | int | продолжительность звонка, сек |
| manager_id | int, FK → managers.id | менеджер |
| call_link | str | путь к файлу записи звонка в /files |

### call_summaries (Сводки звонков)
| Поле | Тип | Описание |
|---|---|---|
| id | int, PK | идентификатор |
| call_id | int, FK → calls.id (unique) | звонок |
| discussion | text | о чём говорили |
| agreements | text | договорённости |
| risks | text | риски / потерянные сделки |

### examples (Примеры)
Названия столбцов и категорий — на английском языке.

| Поле | Тип | Описание |
|---|---|---|
| id | int, PK | идентификатор |
| summary_id | int, FK → call_summaries.id | сводка звонка |
| category | enum: `discussion` \| `agreements` \| `risks` | категория примера |
| text | text | текст примера |

## API

| Метод | Путь | Описание |
|---|---|---|
| GET | `/managers` | список менеджеров |
| GET | `/calls?date_from&date_to&manager_ids=1&manager_ids=2` | список звонков с фильтром по интервалу дат и менеджерам |
| GET | `/calls/{id}/recording` | скачать исходный .docx с расшифровкой звонка |
| GET | `/calls/{id}/summary` | сводка звонка в формате `{discussion: {value, examples}, ...}` |
| GET | `/calls/{id}/summary/export-docx` | скачать оформленный .docx со сводкой звонка |
| POST | `/calls/{id}/summary/upload-docx` | загрузить .docx расшифровки, проанализировать через GenAPI и сохранить сводку |
| GET | `/health` | проверка живости backend |

Фронтенд обращается ко всем эндпоинтам через префикс `/api/...` — это префикс отрезается либо nginx (`nginx.conf`), либо dev-прокси Vite (`vite.config.js`), так что сам backend работает с путями без `/api`.

## Тестовые данные

- 2 менеджера: Иван Иванов, Петр Петров
- 5 звонков:
  - Иванов → **ООО Ромашка** (10.09.2024, 10:00) — первый звонок
  - Иванов → **ООО Ромашка** (15.09.2024, 14:30) — повторный звонок
  - Иванов → **ЗАО Вектор** (20.09.2024, 11:15)
  - Петров → **ООО Технологии** (12.09.2024, 09:45)
  - Петров → **ИП Сидоров** (18.09.2024, 16:00)
- Таблицы `call_summaries` и `examples` заполняются через `POST /calls/{id}/summary/upload-docx`.

## Запуск

### Backend локально (для разработки, без Docker)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # указать GEN_API_KEY
python -m app.init_db       # создать таблицы
python -m app.seed_data     # наполнить тестовыми данными
uvicorn app.main:app --reload
```

Backend поднимется на `http://localhost:8000`.

### Frontend локально (для разработки, без Docker)

```bash
cd frontend
npm install
npm run dev
```

Frontend поднимется на `http://localhost:5173` и будет проксировать `/api/*` на `http://localhost:8000` (см. `vite.config.js`).

### Через Docker Compose (на VPS)

```bash
docker compose up -d --build
docker compose exec backend python -m app.init_db
docker compose exec backend python -m app.seed_data
```

Frontend (nginx) будет доступен на порту `80`/`5173` (в зависимости от `docker-compose.yml`), backend — на порту `8000`.

## Статус

- [x] Структура проекта и Docker-конфигурация
- [x] Таблицы БД и связи
- [x] Тестовые данные (менеджеры, звонки)
- [x] CRUD-функции по каждой таблице (`backend/app/crud/`)
- [x] Анализ звонка через GenAPI и сохранение сводки (`POST /calls/{id}/summary/upload-docx`)
- [x] Frontend (React + Vite): сайдбар, фильтры, таблица звонков, модалка сводки
- [x] API-роуты FastAPI для фронта (`/managers`, `/calls`, `/calls/{id}/recording`, `/calls/{id}/summary`, `/calls/{id}/summary/export-docx`)
- [ ] Загрузка звонка через интерфейс (кнопка есть, функционал в разработке)