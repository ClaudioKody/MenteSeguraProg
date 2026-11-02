## Mente Segura — Programación II

Esta versión usa ReactJS como frontend principal, Flask como backend/API y SQLite como base
SQL. Conserva el diseño y las funciones de Mente Segura: frase, diario con PIN, chat
preventivo, evolución, biblioteca, ayuda profesional y administración.


## Qué significa cada tecnología

Flask ejecuta el backend y responde la API. React muestra la interfaz principal. SQLite
guarda los datos. API REST es el puente JSON entre React y Flask. OpenAPI describe la API y
Swagger UI permite verla y probarla desde el navegador. pytest prueba el backend y
Vitest/React Testing Library prueba React.


## Primera instalación en Windows PowerShell

Requisitos: Python 3.11 o superior y Node.js LTS. No instalar MongoDB.

Desde la carpeta raíz del proyecto:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Abrir el backend en `http://127.0.0.1:5000`. Para detenerlo, usar `Ctrl+C`.

En una segunda terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abrir la interfaz principal React en `http://127.0.0.1:5173`. El backend debe continuar
funcionando en la primera terminal. `npm install` solo se ejecuta la primera vez o si cambia
`package-lock.json`.

## Próximas ejecuciones

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

## Swagger/OpenAPI

Abrir `http://127.0.0.1:5000/api/docs`. Swagger es la pantalla que documenta y permite probar
la API; no es otra aplicación que haya que instalar. El contrato JSON está en
`http://127.0.0.1:5000/api/openapi.json`.

## Pruebas

Desde la raíz, con `.venv` activo:

```powershell
pytest -q tests
```

Para React:

```powershell
cd frontend
npm test -- --run
npm run build
```

## Credenciales de prueba

Usuario: `sofi@mentesegura.local` / `Sofi123!`.

Administrador: `admin@mentesegura.local` / `Admin123!` / documento `30123456`.

## Patrones de diseño

El backend aplica tres patrones, cada uno en su propia carpeta:

- **Factory** (`services/app_factory.py`): la función `create_app(config)` crea la instancia
  de Flask y le aplica una configuración opcional. Permite arrancar la aplicación en modo
  desarrollo o en modo prueba (`TESTING`) sin duplicar código.
- **Repository** (`repositories/nota_repository.py`): la clase `NotaRepository` reúne las
  consultas SQL de las notas privadas (`listar_por_usuario`, `crear`, `actualizar`,
  `eliminar`). Separa el acceso a datos de las rutas de la API, así que si cambia una consulta
  se modifica un solo lugar.
- **Strategy** (`strategies/chat_strategy.py`): cada respuesta del chat es una estrategia
  intercambiable (`RiesgoCriticoStrategy`, `BienestarStrategy` y `ExploracionStrategy`). La
  función `seleccionar_estrategia(nivel, estado)` elige cuál usar según el nivel de riesgo
  detectado y el estado de ánimo. Agregar un nuevo tipo de respuesta solo requiere crear una
  clase nueva.

Los tres patrones se verifican en `tests/test_patterns.py`.

## Seguridad

Mente Segura maneja información personal y emocional, por eso se aplicaron estas medidas:

- **Contraseñas con hash:** se guardan con `generate_password_hash` de Werkzeug, nunca en
  texto plano.
- **Roles y permisos:** el administrador inicia sesión por separado (casilla "Soy
  Administrador" y número de documento). Las funciones administrativas validan `rol = 'admin'`.
  La API responde 401 si no hay sesión y 403 si el rol no tiene permiso.
- **Diario con PIN:** el Diario emocional tiene una segunda protección. El PIN se vuelve a pedir
  al cerrar sesión, al volver a Frase del día o al reiniciar Flask.
- **Límite de intentos de login:** `services/login_guard.py` bloquea el acceso durante cinco
  minutos tras cinco intentos fallidos en diez minutos, para frenar ataques de fuerza bruta.
- **Consultas parametrizadas:** los datos recibidos nunca se concatenan en el SQL, lo que
  previene la inyección SQL. Las plantillas Jinja2 escapan automáticamente el contenido
  ingresado por el usuario.
- **CORS restringido:** la API solo acepta pedidos del frontend de desarrollo
  (`http://127.0.0.1:5173` y `http://localhost:5173`).
- **Privacidad de los datos:** notas, chat y estados de ánimo se consultan siempre filtrados por
  `id_usuario`. El administrador solo ve métricas anónimas y nunca accede a diarios ni a
  conversaciones privadas.
- **Secretos y alertas:** la clave de sesión se lee de la variable `MENTE_SEGURA_SECRET` (ver
  `.env.example`) y `mentesegura.db` está excluida del repositorio en `.gitignore`. Las alertas
  de crisis son simuladas: se registran en la base y no se envían SMS reales.

Antes de publicar en producción: servir con HTTPS y cookies seguras, definir una
`MENTE_SEGURA_SECRET` propia, cambiar las credenciales de prueba, limitar CORS al dominio real
del frontend y guardar el registro de intentos de login de forma persistente, sin almacenar
contraseñas.

## Arquitectura y entrega

La API incluye autenticación, diario, chat, evolución, biblioteca, ayuda y endpoints
administrativos. Se documentan Factory, Repository y Strategy. La documentación completa está
en `docs/Documentacion-MenteSegura-Programacion-II.pdf` y el código fuente Markdown que la
origina. Las capturas reales de Wireshark y los archivos propios del grupo —historias de
usuario y diagrama de clases— deben agregarse antes de entregar.