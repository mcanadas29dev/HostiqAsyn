# Cpomando para arrancar en puerto 8150
uvicorn app.main:app --host 0.0.0.0 --port 8150 --reload

# Para generar una clave de app
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Flujo de trabajo: Desarrollo → GitHub → Docker Hub - Despliegue
Paso 1 — Modificas código en local
Paso 2 — Haces commit y push a GitHub
Paso 3 — GitHub Actions construye y sube la imagen (automático)
    La sube a mcanadas29dev/proyecto con dos tags:
        - latest (mutable, siempre apunta al último build de main).
        - El SHA corto del commit (inmutable, trazable a ese código exacto).
Paso 4 — Verificas en GitHub Actions (opcional pero recomendado)
Paso 5 — Verificas en Docker Hub
Paso 6 — Despliegas en el servidor (cuando quieras actualizar)
    # Opción A: traer el último latest (desarrollo)
    docker-compose pull
    docker-compose up -d

    # Opción B: fijar una versión concreta por SHA (producción)
    # Editas docker-compose.yml para usar: mcanadas29dev/proyecto:<sha-corto>
    docker-compose pull
    docker-compose up -d

# Nota sobre el tag latest
latest es cómodo para desarrollo, pero no es una versión. Es solo el tag por defecto que Docker asigna cuando no especificas otro. Para producción o para poder volver atrás con precisión, usa el tag del SHA del commit (ej. mcanadas29dev/proyecto:a1b2c3d). Ese tag no cambia nunca, así que sabes exactamente qué código estás desplegando.
