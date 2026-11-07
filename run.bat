@echo off
call .venv\Scripts\activate

set PATH=C:\Program Files\PostgreSQL\18\bin;%PATH%
set PSYCOPG_IMPL=python

start http://127.0.0.1:8000/docs
python -m uvicorn main:app --reload

pause