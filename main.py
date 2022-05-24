from sweater import server, dash_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

if __name__ == '__main__':

    app = DispatcherMiddleware(server, {'/dash': dash_app.server})

    run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)
