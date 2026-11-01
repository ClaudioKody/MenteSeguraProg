# API REST y Swagger/OpenAPI
El backend Flask expone JSON bajo `/api`. La documentación interactiva se abre en
`http://127.0.0.1:5000/api/docs` y el contrato en `http://127.0.0.1:5000/api/openapi.json`.
| Método | Ruta | Permiso | Uso |
|---|---|---|---|
| GET | `/api/health` | Público | Comprobar disponibilidad |
| POST | `/api/login` | Público | Iniciar sesión y crear cookie |
| POST | `/api/logout` | Sesión | Cerrar sesión |
| GET | `/api/me` | Sesión | Consultar usuario actual |
| GET | `/api/frases` | Usuario | Obtener frase del día |
| GET/POST | `/api/notas` | Usuario | Listar o crear notas propias |
| GET/POST | `/api/chat` | Usuario | Historial o mensaje preventivo |
| GET | `/api/evolucion` | Usuario | Consultar estados y actividad |
| GET | `/api/biblioteca` | Usuario o admin | Consultar recursos |
| GET | `/api/ayuda` | Usuario o admin | Consultar ayuda profesional |
La API aplica la sesión Flask existente y filtra las notas y mensajes por el usuario
autenticado. El administrador no recibe endpoints para consultar diarios o chats privados.