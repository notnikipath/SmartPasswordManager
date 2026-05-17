# User Manual

## 1. First launch

1. Open the app.
2. Create master password on first launch.
3. Use this master password for all future logins.

## 2. Managing records

- `Добавить`: create new password entry.
- `Редактировать`: update selected entry.
- `Удалить`: remove selected entry.
- `Поиск`: filter by title.
- Category panel: filter by group (`Соцсети`, `Банки`, `Работа`, `Личное`).

## 3. Password generation

- Open `Генератор` from toolbar.
- Set length and character sets.
- Generate password and use it directly.

## 4. Clipboard usage

- Copy login/password from detail panel.
- Clipboard is automatically cleared after timeout for security.

## 5. Vulnerability analysis

- Run `Анализ уязвимостей`.
- App will show:
  - weak passwords
  - repeated passwords across entries

## 6. Encrypted export

1. Click `Экспорт`.
2. Enter export password.
3. Save `.spmx` encrypted file.

## 7. Data location

By default data is in user home directory (`.smart_password_manager`) unless `SPM_DATA_DIR` is set.
