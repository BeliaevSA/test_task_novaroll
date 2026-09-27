"""
Клиент для анализа расшифровки телефонного звонка через GenAPI
(модель gemini-3-5-flash-lite, доступ через прокси-эндпоинт GenAPI,
OpenAI-совместимый клиент — по той же схеме, что и _call_ai_vision
в других частях проекта).
"""

import asyncio
import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.schemas import CallAnalysisResult

logger = logging.getLogger(__name__)

AI_MODEL = 'gemini-3-5-flash-lite'
AI_REQUEST_TIMEOUT = 120
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5


CALL_SUMMARY_PROMPT = """Ниже приведена расшифровка телефонного разговора между менеджером и клиентом.
Проанализируй её и верни результат СТРОГО в виде ОДНОГО JSON-объекта — без пояснений
до или после, без markdown-разметки, без обрамления в ```.

Формат JSON должен быть ТОЧНО таким (названия полей не менять):
{
  "discussion": {
    "value": "",
    "examples": ["", "", "..."]
  },
  "agreements": {
    "value": "",
    "examples": ["", "", "..."]
  },
  "risks": {
    "value": "",
    "examples": ["", "", "..."]
  }
}

Пояснения по полям:
- discussion.value — главное содержание разговора: о чём в целом шла речь.
- agreements.value — договорённости: о чём конкретно договорились по итогам звонка
  (следующие шаги, сроки, условия и т.п.). Если договорённостей не было — прямо укажи это.
- risks.value — риски и потерянные сделки: появились ли риски по сделке, есть ли признаки,
  что сделка сорвалась, приостановлена или клиент отказался. Если рисков нет — прямо укажи это.
- В "examples" каждой категории передай МАССИВ ИЗ НЕ БОЛЕЕ 5 СТРОК — это дословные фрагменты
  расшифровки, скопированные ТОЧНО, без единого изменения слов, порядка слов, пунктуации
  или сокращений. Эти фрагменты должны быть прямым подтверждением вывода в "value" —
  никакого пересказа, только точная вырезка из текста разговора.
- Если для категории нет подходящего фрагмента — верни пустой массив [].
- Не добавляй никаких дополнительных полей, кроме перечисленных выше.

Расшифровка разговора:
\"\"\"
{transcript_text}
\"\"\"
"""


def _strip_code_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('```'):
        raw = raw.split('```', 2)[1]
        if raw.startswith('json'):
            raw = raw[4:]
        raw = raw.strip()
    if raw.endswith('```'):
        raw = raw[:-3].strip()
    return raw


async def analyze_call_transcript(
    transcript_text: str,
    id_call: int | str,
) -> tuple[dict | None, str | None]:
    """
    Отправляет расшифровку звонка в GenAPI (gemini-3-5-flash-lite) и
    возвращает провалидированный словарь вида
    {"discussion": {...}, "agreements": {...}, "risks": {...}}.

    Схема ровно та же, что и в _call_ai_vision: 3 попытки с паузой 5с.
    Возвращает (parsed_dict, None) при успехе или (None, error_message) при неудаче.
    """

    prompt = CALL_SUMMARY_PROMPT.replace('{transcript_text}', transcript_text)
    content = [{'type': 'text', 'text': prompt}]

    last_error = None
    client = AsyncOpenAI(
        base_url='https://proxy.gen-api.ru/v1',
        api_key=settings.GEN_API_KEY,
        default_headers={
            'HTTP-Referer': 'https://es-market.online',
            'X-Title': 'ES-Market',
        },
        timeout=AI_REQUEST_TIMEOUT,
        max_retries=0,
    )
    try:
        for attempt in range(MAX_ATTEMPTS):
            try:
                response = await client.chat.completions.create(
                    model=AI_MODEL,
                    response_format={'type': 'json_object'},
                    messages=[{'role': 'user', 'content': content}],
                    temperature=0.1,
                )
                raw = (response.choices[0].message.content or '').strip()
                raw = _strip_code_fence(raw)

                parsed = json.loads(raw)

                # Модель иногда оборачивает объект в список: [{...}]
                if isinstance(parsed, list):
                    parsed = next((x for x in parsed if isinstance(x, dict)), None)

                if not isinstance(parsed, dict):
                    raise ValueError(
                        f'Ожидался JSON-объект, получено: {type(parsed).__name__}'
                    )

                # Валидация по ожидаемой схеме discussion/agreements/risks
                validated = CallAnalysisResult.model_validate(parsed)
                return {
                    'discussion': validated.discussion.model_dump(),
                    'agreements': validated.agreements.model_dump(),
                    'risks': validated.risks.model_dump(),
                }, None

            except Exception as e:
                last_error = f'{type(e).__name__}: {e}'
                logger.warning(
                    f'[call_summary] AI попытка {attempt + 1}/{MAX_ATTEMPTS} '
                    f'для call_id={id_call}: {last_error}'
                )
                if attempt < MAX_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_DELAY_SECONDS)

        logger.error(
            f'[call_summary] AI не смог обработать call_id={id_call} '
            f'после {MAX_ATTEMPTS} попыток: {last_error}'
        )
        return None, last_error
    finally:
        await client.close()