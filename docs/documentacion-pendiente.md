# Documentación pendiente de completar
## Ya existente en el proyecto del grupo
- Descripción general de Mente Segura.
- Historias de usuario y diagrama de clases: conservar los archivos originales del grupo y
agregarlos a `docs/` si no están en el repositorio.
## Completar para Programación II
- Arquitectura Flask + API + React.
- Tabla de roles y permisos.
- Endpoints y capturas de `/api/docs`.
- Explicación de Factory, Repository y Strategy.
- Medidas de seguridad.
- Pruebas unitarias y de integración.
- Evidencia de Wireshark con datos ficticios.
- Integrantes y responsabilidades.
- Instrucciones de ejecución.
## Historias de usuario que deben coincidir con el código
- Como usuario, quiero guardar una nota privada para registrar cómo me siento.
- Como usuario, quiero conversar con un chat preventivo y recibir recomendaciones.
- Como usuario, quiero descargar y compartir una frase motivacional.
- Como administrador, quiero gestionar Biblioteca y Ayuda profesional sin acceder a contenido
privado.
## Diagrama sugerido
`Usuario 1──N Nota`, `Usuario 1──N MensajeChat`, `Usuario 1──N EstadoAnimo`, `Usuario 1──N
AlertaCrisis`; `Administrador` gestiona `RecursoBiblioteca` y `AyudaProfesional`.