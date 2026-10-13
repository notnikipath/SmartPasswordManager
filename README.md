# Smart Password Manager (Task_3)

Безопасное настольное приложение для хранения, генерации и управления паролями.

## Стек

- Python 3.11
- PyQt6 (GUI)
- SQLCipher (зашифрованная SQLite БД)
- cryptography (AES-256-GCM)

Примечание: локально на Python 3.13 пакет SQLCipher может не собраться, поэтому для гарантированной SQLCipher-конфигурации используйте Docker-образ (там Python 3.11).

## Реализовано по ТЗ

### Обязательная часть

- Окно входа с мастер-паролем
- Главное окно с таблицей записей и панелью категорий
- Просмотр/редактирование выбранной записи
- CRUD-операции для записей
- Поиск и фильтрация
- Генератор паролей
- Индикатор силы пароля
- Копирование логина/пароля в буфер
- Экспорт в зашифрованный формат `.spmx`
- PBKDF2-хэш мастер-пароля + соль
- AES-256-GCM шифрование полей
- SQLCipher ключ для локальной БД
- Параметризованные SQL-запросы

### Дополнительные улучшения

1. Аудит безопасности (успешные/неуспешные входы, CRUD, экспорт)
2. Автоочистка буфера обмена через N секунд
3. Усиленная KDF схема (PBKDF2 с солью и большим числом итераций)
4. Анализ уязвимостей (слабые и повторяющиеся пароли)

## Структура

```text
Task_3/
├── src/
│   ├── core/
│   │   ├── crypto/
│   │   ├── database/
│   │   ├── models/
│   │   └── services/
│   ├── ui/
│   │   ├── windows/
│   │   ├── dialogs/
│   │   ├── controls/
│   │   └── styles/
│   └── utils/
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
```

## Локальный запуск

```bash
cd Task_3
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/app.py
```

## Docker

### Сборка

```bash
docker compose build
```

### Запуск (GUI в браузере)

```bash
docker compose up -d
```

После запуска откройте в браузере:

```text
http://localhost:18080/vnc.html
```

Откроется noVNC, через который доступно окно приложения.

Если порт занят, можно выбрать другой:

```powershell
$env:SPM_WEB_PORT="6090"
docker compose up -d
```

### Важно по безопасности

В Docker включен строгий режим `SPM_REQUIRE_SQLCIPHER=1`: если SQLCipher недоступен, приложение не запустится (без fallback на обычный `sqlite3`).

## Проверка

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Документация

- `docs/security.md` — принятые меры безопасности
- `docs/user_manual.md` — руководство пользователя

## Windows: SQLCipher

`sqlcipher3-binary` has no Windows wheel and is installed only on non-Windows systems. On Windows the application can run with SQLite: credential fields remain encrypted with AES-256-GCM, but the database file and entry titles are not encrypted. The login window explicitly displays this limitation. For mandatory whole-database encryption, install a compatible SQLCipher driver or use the Docker setup with `SPM_REQUIRE_SQLCIPHER=1`; this setting rejects an unencrypted database fallback.
