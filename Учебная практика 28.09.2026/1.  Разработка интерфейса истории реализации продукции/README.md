## Описание структуры приложения

- `import_data/` — папка со встроенными сырыми данными для миграции:
  - `import_partners.csv` — список контрагентов компании.
  - `import_sales.txt` — история продаж (разделитель — табуляция).
- `main.py` — главный исполняемый файл приложения (содержит парсер `.env`, SQL-запрос к БД, бизнес-логику расчета скидок и UI-интерфейс на Tkinter).
- `.env` — файл с секретными доступами и конфигурацией подключения к вашей базе данных PostgreSQL.
- `query.sql` — SQL-скрипт с тестовыми запросами для ручной проверки смены скидок.
- `schema.sql` — скрипт инициализации структуры БД и автоматического импорта файлов из папки `import_data`.
- `README.md` — руководство по приложению.

## Как запустить приложение

### 1. Настройка и наполнение базы данных

Перед запуском приложения примените скрипты инициализации в вашей СУБД **PostgreSQL**.

Сначала примените основную структуру и импорт данных (`schema.sql`). Затем для работы калькулятора материалов выполните в SQL-консоли следующий скрипт создания справочников:

```sql
   -- 1. Создаем справочник типов продукции
   CREATE TABLE IF NOT EXISTS product_types (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      product_type_coefficient NUMERIC(5, 2) NOT NULL
   );

   -- 2. Создаем справочник типов материалов
   CREATE TABLE IF NOT EXISTS material_types (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      scrap_percentage NUMERIC(5, 2) NOT NULL
   );

   -- 3. Наполняем тестовыми данными для калькулятора (ID: 1 и 2)
   INSERT INTO product_types (id, name, product_type_coefficient) VALUES
   (1, 'Двери', 1.05),
   (2, 'Окна', 1.20)
   ON CONFLICT (id) DO NOTHING;

   INSERT INTO material_types (id, name, scrap_percentage) VALUES
   (1, 'Древесина', 0.50),
   (2, 'Пластик', 1.10)
   ON CONFLICT (id) DO NOTHING;
```

2. **Заполните `.env`**: укажите доступы к вашей локальной СУБД в файле `.env`:

   ```env
   DB_NAME=имя_базы
   DB_USER=пользователь
   DB_PASSWORD=пароль
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Установите зависимости**:

   ```bash
   python -m pip install psycopg2-binary
   ```

4. **Запустите приложение**:
   ```bash
   python main.py
   ```
