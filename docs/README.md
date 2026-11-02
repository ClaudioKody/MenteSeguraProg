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
.\\.venv\\Scripts\\Activate.ps1 
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
.\\.venv\\Scripts\\Activate.ps1 
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
 
## Arquitectura y entrega 
 
La API incluye autenticación, diario, chat, evolución, biblioteca, ayuda y endpoints 
administrativos. Se documentan Factory, Repository y Strategy. La documentación completa está 
en `docs/Documentacion-MenteSegura-Programacion-II.pdf` y el código fuente Markdown que la 
origina. Las capturas reales de Wireshark y los archivos propios del grupo —historias de 
usuario y diagrama de clases— deben agregarse antes de entregar.  
