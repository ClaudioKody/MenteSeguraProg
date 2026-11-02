from flask import jsonify, Response

OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "Mente Segura API", "version": "1.0.0", "description": "API preventiva para frases, diario, chat y evolución. No reemplaza atención profesional."},
    "servers": [{"url": "/"}],
    "tags": [{"name": "Autenticación"}, {"name": "Usuario"}, {"name": "Chat preventivo"}],
    "paths": {
        "/api/health": {"get": {"tags": ["Usuario"], "summary": "Comprobar disponibilidad", "responses": {"200": {"description": "Servicio disponible"}}}},
        "/api/login": {"post": {"tags": ["Autenticación"], "summary": "Iniciar sesión", "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Login"}}}}, "responses": {"200": {"description": "Sesión iniciada"}, "401": {"description": "Credenciales inválidas"}}}},
        "/api/logout": {"post": {"tags": ["Autenticación"], "summary": "Cerrar sesión", "responses": {"200": {"description": "Sesión cerrada"}}}},
        "/api/me": {"get": {"tags": ["Autenticación"], "summary": "Usuario actual", "responses": {"200": {"description": "Perfil"}, "401": {"description": "No autenticado"}}}},
        "/api/frases": {"get": {"tags": ["Usuario"], "summary": "Obtener frase del día", "responses": {"200": {"description": "Frase"}, "401": {"description": "No autenticado"}}}},
        "/api/notas": {"get": {"tags": ["Usuario"], "summary": "Listar notas privadas", "responses": {"200": {"description": "Notas del usuario"}}}, "post": {"tags": ["Usuario"], "summary": "Crear nota privada", "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Nota"}}}}, "responses": {"201": {"description": "Nota creada"}, "400": {"description": "Datos inválidos"}}}},
        "/api/chat": {"get": {"tags": ["Chat preventivo"], "summary": "Historial privado"}, "post": {"tags": ["Chat preventivo"], "summary": "Enviar mensaje y detectar riesgo", "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Mensaje"}}}}, "responses": {"200": {"description": "Respuesta preventiva"}}}},
        "/api/evolucion": {"get": {"tags": ["Usuario"], "summary": "Consultar evolución"}},
        "/api/biblioteca": {"get": {"tags": ["Usuario"], "summary": "Consultar biblioteca"}},
        "/api/ayuda": {"get": {"tags": ["Usuario"], "summary": "Consultar ayuda profesional"}}
    },
    "components": {"schemas": {"Login": {"type": "object", "required": ["email", "password"], "properties": {"email": {"type": "string", "format": "email"}, "password": {"type": "string"}, "documento": {"type": "string"}}}, "Nota": {"type": "object", "required": ["texto"], "properties": {"titulo": {"type": "string"}, "texto": {"type": "string", "maxLength": 5000}, "estado_animo": {"type": "string"}}}, "Mensaje": {"type": "object", "required": ["mensaje"], "properties": {"mensaje": {"type": "string", "maxLength": 1000}}}}}
}

OPENAPI["paths"].update({
    "/api/auth/registro": {"post": {"tags": ["Autenticación"], "summary": "Registrar usuario"}},
    "/api/auth/login": {"post": {"tags": ["Autenticación"], "summary": "Iniciar sesión React"}},
    "/api/auth/logout": {"post": {"tags": ["Autenticación"], "summary": "Cerrar sesión React"}},
    "/api/diario/pin": {"post": {"tags": ["Usuario"], "summary": "Abrir diario con PIN"}},
    "/api/notas/{id}": {"put": {"tags": ["Usuario"], "summary": "Editar nota propia"}, "delete": {"tags": ["Usuario"], "summary": "Eliminar nota propia"}},
    "/api/chat": {"delete": {"tags": ["Chat preventivo"], "summary": "Limpiar historial privado"}},
    "/api/admin": {"get": {"tags": ["Administración"], "summary": "Consultar datos administrativos"}},
    "/api/admin/biblioteca/{id}": {"put": {"tags": ["Administración"], "summary": "Editar recurso"}, "delete": {"tags": ["Administración"], "summary": "Eliminar recurso"}},
    "/api/admin/ayuda/{id}": {"put": {"tags": ["Administración"], "summary": "Editar ayuda profesional"}, "delete": {"tags": ["Administración"], "summary": "Eliminar ayuda profesional"}}
})

def register_docs(app):
    @app.get("/api/openapi.json")
    def openapi_json():
        return jsonify(OPENAPI)

    @app.get("/api/docs")
    def swagger_docs():
        html = """<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Mente Segura API · Swagger</title><link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'></head><body><div id='swagger-ui'></div><script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script><script>window.onload=()->SwaggerUIBundle({url:'/api/openapi.json',dom_id:'#swagger-ui',deepLinking:true,presets:[SwaggerUIBundle.presets.apis,SwaggerUIBundle.SwaggerUIStandalonePreset],layout:'StandaloneLayout'});</script></body></html>"""
        return Response(html, mimetype="text/html")
    return app