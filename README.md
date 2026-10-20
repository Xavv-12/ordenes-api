# ordenes-api

## Práctica 1 · Tabla del paso 4

| Petición | Código de estado | Mensaje (detail) | ¿Quién generó el error? |
|---|---|---|---|
| GET /cuadrado/abc | 422 Unprocessable Entity | Input should be a valid integer, unable to parse string as an integer | FastAPI (validación con Pydantic): `n` está declarado como `int` y "abc" no se puede convertir. La función nunca se ejecutó. |
| GET /no-existe | 404 Not Found | Not Found | FastAPI (el enrutador): no existe ninguna ruta con ese path. |
| POST /health | 405 Method Not Allowed | Method Not Allowed | FastAPI (el enrutador): la ruta existe, pero solo acepta GET (cabecera `allow: GET`). |
| GET /saludo/Ana?mayusculas=quizas | 422 Unprocessable Entity | Input should be a valid boolean, unable to interpret input | FastAPI (validación con Pydantic): `mayusculas` está declarado como `bool` y "quizas" no es un booleano válido. |

Capturas en la carpeta `evidencias/`.