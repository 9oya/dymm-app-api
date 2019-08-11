def register_blueprint(app):
    from views import test_view
    from apis import api

    app.register_blueprint(test_view)
    app.register_blueprint(api)
