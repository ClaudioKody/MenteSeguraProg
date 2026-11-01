# Mente Segura — Documentación técnica para Programación II
## Alcance
Mente Segura conserva su dominio de bienestar emocional: frases, diario privado, chat
preventivo, alertas, respiración, evolución, biblioteca y ayuda profesional. No realiza
diagnósticos ni reemplaza atención profesional.
## Arquitectura
- **Backend:** Flask, SQLite y API REST JSON.
- **Frontend principal:** ReactJS con Vite, organizado como SPA y consumidor exclusivo de
`/api/*` para las pantallas de la entrega.
- **Compatibilidad:** las plantillas Jinja2 antiguas permanecen únicamente como respaldo
interno del backend y no forman parte de la interfaz React presentada.
- **Datos:** SQLite con consultas parametrizadas. La consigna impresa menciona MongoDB, pero
el equipo utiliza SQL por indicación docente y por ser la tecnología trabajada.
- **Documentación:** OpenAPI disponible en `/api/openapi.json` y Swagger UI en `/api/docs`.
## Roles y permisos
- **Usuario:** accede a sus frases, notas, chat, evolución, biblioteca y ayuda. Nunca puede
consultar registros de otro usuario.
- **Administrador:** gestiona Biblioteca y Ayuda profesional y consulta métricas anónimas. No
accede a diarios ni conversaciones privadas.
## Patrones de diseño
1. **Factory:** `services/app_factory.py` centraliza la creación/configuración de una
instancia Flask para desarrollo y pruebas.
2. **Repository:** `repositories/nota_repository.py` encapsula las consultas de notas y
separa persistencia de las rutas.
3. **Strategy:** `strategies/chat_strategy.py` permite intercambiar la respuesta preventiva
según el contexto, por ejemplo riesgo crítico o bienestar positivo.
## Seguridad existente y agregada
Las contraseñas se almacenan con hash Werkzeug, las consultas usan parámetros, las rutas
validan sesión/rol y los registros privados filtran por `id_usuario`. La API devuelve 401
cuando no hay sesión. Los secretos se leen desde variables de entorno cuando corresponde.
Para producción se debe servir con HTTPS, usar una `MENTE_SEGURA_SECRET` propia y no publicar
credenciales de prueba.
## Pruebas
Ejecutar `pytest -q tests`. Incluye pruebas unitarias de detección de riesgos y estados de
ánimo, además de pruebas de integración de autenticación, permisos, health check y
documentación OpenAPI.
## Wireshark pendiente
La captura real se realiza en la computadora del equipo con datos ficticios. Documentar login
o una petición `/api`, protocolo observado, filtro aplicado, ausencia de credenciales reales
y diferencia entre HTTP local y HTTPS/TLS en producción.
