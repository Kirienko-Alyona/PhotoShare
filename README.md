# PhotoShare
1. Для розгортання додатку локально на комп'ютері потрібно створити базу даних *Postges*, наприклад в *DBeaver*.
2. Встановити пакет віртуального оточення *poetry*
3. Створити *".env"* файл на основі *"example.env"*
4. Встановити Docker(desktop), Redis(web), якщо Redis(desktop), то треба закоментувати "redis_password" в main.py, src/services/auth.py
5. Запустити середовище розробки 
6. В терміналі виконати команду **alembic upgrade heads**
7. В терміналі виконати команду **docker-compose up**
8. Також в терміналі запустити серевер командою **uvicorn main:app --host localhost --port 8000 --reload** або **uvicorn main:app --reload**
9. Відкрити сторінку в браузері за посиланням з термінала.
