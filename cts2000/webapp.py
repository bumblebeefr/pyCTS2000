import logging
import argparse
from flask import Flask, Response, request, redirect, render_template, abort, make_response, flash, jsonify, send_file
import simplejson
import traceback
import argparse

from cts2000 import CTS2000

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--host', type=str, default="0.0.0.0")
    parser.add_argument('--type', type=str, choices=['usb', 'serial'], default='serial')
    parser.add_argument('--device', type=str, default='/dev/ttyUSB0')
    args = parser.parse_args()

    app = Flask(__name__)
    app.secret_key = 'euGh4eirniw7ot2Rieta8Ahpshuu7ahMTaigae2aOhZ6eichtee3liuJKieki5ci'

    if args.type == 'serial':
        printer = CTS2000(serialDevice=args.device)
    else:
        printer = CTS2000(usbDevice=args.device)

    def _execute(method_name, args, kwargs):
        if(method_name.startswith("_")):
            raise ValueError("Can't use system or hidden methods with the api")
        getattr(printer, method_name)(*args, **kwargs)

    @app.route('/')
    def home():
        return render_template("index.html", urls="")

    @app.route('/api/do/<method_name>', methods=['GET', 'POST'])
    def api_execmethod(method_name):
        try:
            data = {}
            if request.method == 'POST':
                if request.data.strip():
                    data = simplejson.loads(request.data)
            response = _execute(method_name, data.get('args', []), data.get('kwargs', {}))
            return jsonify(response=response)
        except:
            logger.exception("Exception occurs on api call")
            return Response(
                response=simplejson.dumps({
                    "error": traceback.format_exc(),
                    "method_name": method_name,
                    "data": data
                }),
                status=400,
                content_type='application/json')

    @app.route('/api/do', methods=['POST'])
    def api_do():
        data = request.data
        try:
            data = simplejson.loads(request.data)
            if isinstance(data, dict):
                data = [data]
            for command in data:
                _execute(command.get("do", ""), command.get('args', []), command.get('kwargs', {}))
            return jsonify()
        except:
            printer.cut()
            logger.exception("Exception occurs on api call")
            return Response(
                response=simplejson.dumps({
                    "error": traceback.format_exc(),
                    "data": data
                }),
                status=400,
                content_type='application/json')

    logger.info('Starting on http://%s:%s' % (args.host, args.port))
    app.run(host=args.host, port=args.port, threaded=False, debug=True)


if __name__ == '__main__':
    main()
