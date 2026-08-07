---
name: bcp-workflow
description: "Proyecto BCP-Organizate: procesamiento de extractos bancarios (BCP débito, BCP crédito, Yape), arquitectura limpia (Aframework/Capplication/Denterprise), FastAPI + PostgreSQL + Next.js. Usar cuando: agregar un nuevo parser de banco, crear un nuevo caso de uso, entender el flujo completo de importación de transacciones, arrancar servicios, trabajar con archivos cifrados, o navegar la arquitectura del proyecto."
argument-hint: "Describe qué quieres hacer: agregar parser, caso de uso, arrancar servicios, etc."
---

# BCP-Organizate Workflow

Reemplazo de la app BCP-Organizate. Extrae y categoriza transacciones de extractos bancarios (PDF/CSV) de BCP débito, BCP crédito y Yape.

## Arquitectura (Clean Architecture)

```
new-service/
├── src/
│   ├── Aframework/        # Frameworks & Drivers: FastAPI routes, DB gateways, parsers
│   ├── Capplication/      # Application: Use Cases y DTOs
│   └── Denterprise/       # Enterprise: Entities y reglas de negocio
├── app/
│   ├── api/routes/        # Rutas FastAPI (delgadas, llaman Use Cases)
│   └── main.py
```

Flujo de una petición:
```
FastAPI route → UseCase (DTO Request) → Gateway ↔ Entity → UseCase → DTO Response → FastAPI
```

Los DTOs de FastAPI se usan directamente en las rutas (sin capa de Interface Adapters) para generar documentación Swagger automáticamente.

## Arrancar el Proyecto

### Local (desarrollo activo)

```sh
cd new-service
poetry install
poetry env info        # copiar el path del entorno y seleccionarlo en VS Code
# F5 para lanzar FastAPI (launch.json ya configurado)

# Frontend Streamlit (opcional)
poetry run streamlit run src/Aframework/app.py
```

### Docker (entorno completo)

```sh
# Levantar todo
docker compose up

# Solo DB + servicio (sin frontend ni pgadmin)
docker compose up db new-service

# Reiniciar DB desde cero
docker compose down db -v
docker compose up db -d
docker compose up new-service-init --build
```

Servicios disponibles:
| Servicio | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Streamlit | http://localhost:8501 |
| Next.js | http://localhost:3000 |
| pgAdmin | http://localhost:80 |

## Flujo de Importación de Transacciones

### Caso 1: Proyecto vacío (primera vez)

1. `POST /documents` — crear documento con el archivo del banco
2. `POST /transactions` — extraer transacciones del documento (usar el `id` devuelto)
3. `PUT /transactions/{id}` — categorizar cada transacción
4. `GET /transactions/export` — exportar a CSV

### Caso 2: Proyecto reiniciado (ya hay CSVs)

1. `POST /documents` (uno por cada archivo)
2. `GET /documents` — obtener los IDs
3. `POST /transactions/import` — importar desde CSV

Ver flujo completo en [REST/README.md](../../new-service/REST/README.md) y los archivos `.http` en `new-service/REST/`.

## Parsers de Bancos

Los parsers viven en `src/Aframework/gateway/content_extractor/`:

| Archivo | Banco |
|---|---|
| `bcp_debit_parser.py` | BCP Débito |
| `bcp_credit_parser.py` | BCP Crédito |
| `yape_parser.py` | Yape |

### Agregar un nuevo parser

1. Crear `src/Aframework/gateway/content_extractor/<banco>_parser.py` implementando la interfaz de parser existente.
2. Registrarlo en `app/api/routes/document.py` junto a los otros parsers.
3. Agregar el nuevo `document_format` en `init_data.py` si aplica.

## Agregar un Nuevo Caso de Uso

1. Crear entidad en `src/Denterprise/` si es un concepto nuevo.
2. Crear DTO en `src/Capplication/DTO/<entidad>_dto.py`.
3. Crear use case en `src/Capplication/use_cases/<entidad>/<nombre>.py`.
4. Crear gateway en `src/Aframework/gateway/db/<entidad>.py` si necesita acceso a DB.
5. Exponer en `app/api/routes/<entidad>.py` (ruta FastAPI delgada).
6. Registrar el router en `app/api/main.py`.

## Archivos Cifrados (SOPS + age)

Los archivos CSV sensibles en `files/exports/` se cifran en `files/exports-enc/`.

```sh
# Descifrar
SOPS_AGE_KEY_FILE=../key.txt ./scripts/enc.sh decrypt

# Cifrar
SOPS_AGE_KEY_FILE=../key.txt ./scripts/enc.sh encrypt
```

La clave `key.txt` se encuentra un nivel arriba del workspace y **no se versiona**.

## Herramientas de Calidad

```sh
# Detectar código muerto
vulture .

# Formatear código
poetry run black .
```

## Variables de Entorno Requeridas

```
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_PORT
POSTGRES_SERVER
PDF_PASSWORD        # contraseña de los PDFs del banco
```

Para Docker, definirlas en un `.env` en la raíz del proyecto.
