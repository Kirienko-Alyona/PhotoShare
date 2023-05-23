# PhotoShare
Для розгортання додатку локально на комп'ютері потрібно створити базу даних *Postges*, наприклад в *DBeaver*.
Встановити пакет віртуального оточення *poetry*
Створити *".env"* файл на основі *"example.env"*
Встановити Docker(desktop), Redis(web)
Запустити середовище розробки 
В терміналі виконати команду **alembic upgrade head**
В терміналі виконати команду **docker-compose up**
Також в терміналі запустити серевер командою **uvicorn main:app --host localhost --port 8000 --reload** або **uvicorn main:app --reload**
Відкрити сторінку в браузері за посиланням з термінала.
