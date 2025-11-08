# BCP PDF Extractor Service

Este servicio extrae datos de transacciones de estados de cuenta PDF del BCP, específicamente las columnas:
- Fecha de proceso
- Fecha de consumo  
- Descripción
- Tipo de Operación
- Soles
- Dólares

## Características

- **API REST** construida con FastAPI
- **Extracción de PDF** usando pdfplumber y tabula-py
- **Limpieza automática** de datos (fechas, montos, texto)
- **Exportación a Excel** con formato
- **Logging** detallado para debugging
- **Dockerizada** para fácil deployment

## Endpoints

### `POST /extract-pdf`
Extrae datos del PDF y retorna JSON con las transacciones.

**Request:**
```bash
curl -X POST "http://localhost:8000/extract-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@EECC102025_09745280.pdf"
```

**Response:**
```json
{
  "message": "Successfully extracted 45 transactions",
  "filename": "EECC102025_09745280.pdf",
  "transactions": [
    {
      "fecha_proceso": "2025-10-01",
      "fecha_consumo": "2025-09-30",
      "descripcion": "COMPRA POS METRO S.A.",
      "tipo_operacion": "CONSUMO",
      "soles": 45.80,
      "dolares": 0.0
    }
  ]
}
```

### `POST /extract-pdf/excel`
Extrae datos del PDF y retorna archivo Excel.

## Uso con Docker

### Construcción
```bash
cd new-service
docker build -t bcp-pdf-extractor .
```

### Ejecución
```bash
docker run -p 8000:8000 bcp-pdf-extractor
```

### Con Docker Compose
```bash
docker-compose up --build
```

## Uso local

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Interfaz Web

Una vez levantado el servicio, puedes acceder a:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estructura del Proyecto

```
new-service/
├── main.py              # Aplicación FastAPI principal
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Imagen Docker
├── docker-compose.yml  # Orquestación
└── README.md           # Esta documentación
```

## Notas Técnicas

- **Formato de fechas**: Se estandarizan a formato ISO (YYYY-MM-DD)
- **Montos**: Se limpian automáticamente (eliminan símbolos de moneda, comas)
- **Encoding**: Soporte para caracteres especiales en español
- **Errores**: Logging detallado para debugging

## Testing

Puedes probar con curl:
```bash
# Extraer a JSON
curl -X POST "http://localhost:8000/extract-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@tu_archivo.pdf"

# Extraer a Excel
curl -X POST "http://localhost:8000/extract-pdf/excel" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@tu_archivo.pdf" \
  --output resultado.xlsx
```