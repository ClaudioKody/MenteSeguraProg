# Seguridad y pruebas
Las contraseñas utilizan hash seguro de Werkzeug. Las consultas SQL usan parámetros y no
concatenan datos recibidos. Las rutas HTML y API requieren sesión, y las funciones
administrativas validan `rol='admin'`. El diario agrega una segunda protección mediante PIN y
sesión específica. La API devuelve 401 para accesos no autenticados y mantiene los datos
privados filtrados por `id_usuario`.
El guardia de login registra fallos en memoria, limita cinco intentos dentro de diez minutos
y bloquea temporalmente durante cinco minutos. En producción se debe persistir el registro de
auditoría sin guardar contraseñas, configurar una clave secreta fuerte mediante
`MENTE_SEGURA_SECRET`, usar HTTPS, cookies seguras y CORS limitado al origen del frontend.
Ejecutar las pruebas con `pytest -q tests`. Las unitarias validan detección crítica,
respuestas del chat y estados positivos. Las de integración validan 401, health, OpenAPI y
carga de la aplicación. Los casos end-to-end recomendados son: login de usuario → frase →
chat → evolución; y login de administrador → editar Biblioteca → comprobar persistencia.