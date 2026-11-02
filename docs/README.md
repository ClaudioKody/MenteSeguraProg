# Mente Segura — Sprint 1 + Sprint 2 
 
Aplicación web construida con Python, Flask, HTML, CSS y SQLite. El diseño visual 
lavanda/rosado, las fotografías, las frases del día y el Diario emocional del Sprint 1 se 
mantienen. 
 
## Sprint 1 conservado 
 - Frase del día con fotografía real, descarga y compartir. - Diario emocional protegido por PIN `1234`. - Crear, visualizar, editar y eliminar notas. - Exportar el registro personal en PDF. - El acceso al Diario vuelve a pedir el PIN al cerrar sesión, volver a Frase del día o 
reiniciar Flask. 
 
## Sprint 2 agregado 
 - Registro de usuarios con nombre, apellido, correo, contraseña y contacto de confianza 
obligatorio. - Inicio de sesión de usuarios. - Inicio de sesión de administrador separado mediante casilla **Soy Administrador** y 
documento obligatorio. - Dashboard administrativo con métricas anónimas y gráfico de crecimiento de usuarios. El 
administrador nunca consulta textos ni diarios privados. - CRUD de Biblioteca Digital: alta, edición y baja de recursos. - CRUD de Ayuda Profesional: alta, edición y baja de teléfonos y centros. - Menú hamburguesa para navegar hacia Biblioteca, Ayuda Profesional y Diario. - Biblioteca con enlaces para ver o descargar recursos. - Ayuda Profesional con enlaces `tel:` para llamar desde un dispositivo móvil. 
 
## Credenciales administrativas de prueba 
 
El administrador se crea automáticamente en SQLite y no puede registrarse desde el formulario 
común: 
 - Correo: `admin@mentesegura.local` - Contraseña: `Admin123!` - Documento: `30123456` 
 
En un entorno real, cambiá estas credenciales y la clave secreta antes de publicar. 
 
## Ejecutar en Windows PowerShell 
 
```powershell 
py -m venv .venv 
.\.venv\Scripts\Activate.ps1 
python -m pip install -r requirements.txt 
python app.py
 
Abrí `http://127.0.0.1:5000`. 
 
## macOS o Linux 
 
```bash 
python3 -m venv .venv 
source .venv/bin/activate 
python -m pip install -r requirements.txt 
python app.py 
``` 
 
La base `mentesegura.db` se crea y migra automáticamente. 
 
## Ver la aplicación en el celular con QR 
 
La computadora y el celular deben estar conectados a la misma red Wi-Fi. Con el entorno 
virtual activo, abrí dos terminales en Visual Studio Code. 
 
En la primera: 
 
```powershell 
python app.py 
``` 
 
En la segunda: 
 
```powershell 
python -m pip install -r requirements.txt 
python mostrar_qr.py 
``` 
 
El script genera `qr-mentesegura.png` y muestra una dirección parecida a 
`http://192.168.1.25:5000`. Abrí la imagen, escaneala con el celular y entrá a la dirección. 
Si Windows pregunta por el firewall, permití el acceso en redes privadas. 
 
## Sprint 3 agregado 
 
El Sprint 3 incorpora un Chat de apoyo preventivo con historial privado por usuario, 
sugerencias dinámicas mientras se escribe y un botón para limpiar toda la conversación. 
También agrega análisis local de mensajes para detectar señales relacionadas con ansiedad 
intensa, depresión, bullying o ideación autolesiva. 
 
Cuando se detecta un nivel crítico, se registra en SQLite una alerta simulada usando el 
número telefónico que el usuario indicó como contacto de confianza. Esta versión no envía SMS 
reales. También se incorpora una respiración guiada interactiva y la sección Mi evolución, 
con resumen semanal, estados de ánimo registrados y refuerzo positivo. 
 
El estado de ánimo puede seleccionarse al guardar una nota del Diario emocional. Si se deja 
vacío, la aplicación intenta detectarlo a partir del texto. El chat es preventivo y no 
reemplaza la atención profesional. Ante un peligro inmediato, la aplicación indica contactar 
al número de confianza o a emergencias. 
 
## Corrección posterior del Sprint 3 
 
El Chat de apoyo ahora responde en varios turnos por cada mensaje, formula preguntas de 
seguimiento y ofrece alternativas de autocuidado según el contexto. Los mensajes de mejoría, 
tristeza o ansiedad también alimentan la sección Mi evolución. La respiración guiada tiene 
pausa y reanudación reales, conservando la fase y el tiempo donde se detuvo. 
 
## Opciones ante una alerta crítica 
 
Cuando el chat detecta una expresión de riesgo crítico, la pantalla muestra tres opciones. 
**Enviar SMS** abre la aplicación de mensajes del celular con un texto preparado para el 
número de confianza, para que la persona lo revise y confirme. **Llamar** abre el marcador 
telefónico con ese número. **Recomendaciones** muestra acciones inmediatas, respiración 
guiada y acceso a Ayuda profesional. En un navegador de computadora estos enlaces dependen de 
que el sistema tenga aplicaciones asociadas a `sms:` y `tel:`; en un celular son las opciones 
nativas del dispositivo. 
 
## Adaptación para Programación II 
 
La copia adaptada conserva la aplicación original y agrega una API REST Flask bajo `/api`, 
documentación OpenAPI/Swagger en `/api/docs`, una base React en `frontend/`, los patrones 
Factory/Repository/Strategy, pruebas en `tests/` y documentación técnica en `docs/`. Ejecutá 
`pytest -q tests` para validar el backend. La captura real de Wireshark queda a cargo del 
grupo con datos ficticios. 