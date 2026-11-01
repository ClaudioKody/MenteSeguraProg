def create_app(config=None):
    """Patrón Factory: crea una instancia Flask configurable para desarrollo y tests."""
    from app import app
    if config:
        app.config.update(config)
    return app
