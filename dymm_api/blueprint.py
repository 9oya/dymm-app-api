def register_blueprint(app):
    from .views import test_view
    from .apis import avt_api, bnr_api, mail_api, tag_api

    app.register_blueprint(test_view)
    app.register_blueprint(avt_api)
    app.register_blueprint(bnr_api)
    app.register_blueprint(mail_api)
    app.register_blueprint(tag_api)
