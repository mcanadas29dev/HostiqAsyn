# Cpomando para arrancar en puerto 8150
uvicorn app.main:app --host 0.0.0.0 --port 8150 --reload

# Para generar una clave de app
python -c "import secrets; print(secrets.token_urlsafe(64))"
