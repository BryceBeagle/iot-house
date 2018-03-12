import json
import logging

from flask import Flask
from flask_sockets import Sockets

from control.idiotic_controller import IdioticController


app = Flask(__name__)
app.config['DEBUG'] = True
socketio = Sockets(app)

logger = logging.getLogger('gunicorn.error')

controller = IdioticController()


@socketio.route('/embedded')
def handle_json(ws):
    """Set or get attribute of IdioticDevice

    json structure:
        {"set" : [
           {
            "id"    : <uuid of IdioticDevice instance>,
            "attr"  : <attribute name>,
            "value" : <value>,
           },
           {
            "class" : <type(IotDevice())>,
            "name"  : <IotDevice().name>,
            "attr"  : <attribute name>,
            "value" : <value>
           }
        ],
        "get : [
           {
            "id"    : <uuid of IotDevice instance>,
            "attr"  : <attribute name>
           },
           {
            "class" : <type(IotDevice())>,
            "name"  : <IotDevice().name>,
            "attr"  : <attribute name>
           }
        ]}

    json contains a list of set and/or get commands. Either id, or class+name, must be specified in json

    :param module_class:
    :return:
    """
    while not ws.closed:
        message = ws.receive()

        print(message)

        req_json = json.loads(message)

        # Module just started up
        if 'hello' in req_json:
            controller.new_ws_device(req_json['class'], req_json['uuid'], ws)

            # TODO: Remove
            configure_events()

        # Otherwise, it needs a set or a get
        elif 'set' not in req_json and 'get' not in req_json:
            print(f"Invalid message: {message}")
            continue

        if 'set' in req_json:
            for attr, value in req_json['set'].items():
                try:
                    getattr(controller[req_json['uuid']], attr).update(value)
                except (AttributeError, TypeError):
                    logging.error(f"Attribute {attr} does not exist or has no update function")


@app.route("/")
def hello():
    return "Hello World"


def configure_events():

    from control.idiotic_routine import IdioticRoutine
    from control.idiotic_trigger import IdioticTrigger
    from control.idiotic_event import IdioticEvent

    from control.idiotic_devices.hue import HueBridge

    HueBridge(controller)

    dr1 = controller.HueLight["Living Room 2"]
    temp_sensor = controller["62:01:94:31:6A:EA"]

    action_warm = [lambda: dr1.brightness.set(254)]
    action_cold = [lambda: dr1.brightness.set(0)]

    event_warm = IdioticEvent(action_warm)
    event_cold = IdioticEvent(action_cold)

    routine_warm = IdioticRoutine(event_warm)
    routine_cold = IdioticRoutine(event_cold)

    trigger_warm = IdioticTrigger(routine_warm, temp_sensor.temp, IdioticTrigger.check_gt, 30)
    trigger_cold = IdioticTrigger(routine_cold, temp_sensor.temp, IdioticTrigger.check_lt, 30)


if __name__ == "__main__":

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    from werkzeug.debug import DebuggedApplication
    from werkzeug.serving import run_with_reloader

    server = pywsgi.WSGIServer(('0.0.0.0', 5000), DebuggedApplication(app, True),
                               handler_class=WebSocketHandler)
    run_with_reloader(server.serve_forever())
