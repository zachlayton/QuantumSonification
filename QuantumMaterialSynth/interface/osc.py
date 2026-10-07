from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer


def start_osc_server(params, callback, host="0.0.0.0", port=7410):
    """
    OSC messages:
        /qmat/base_freq 40
        /qmat/coupling_xx 0.5
        /qmat/coupling_zz 0.2
        /qmat/coupling_dm 0.8
        /qmat/t2 6
        /qmat/render
    """

    dispatcher = Dispatcher()

    def set_param(address, *args):
        name = address.split("/")[-1]

        if not args:
            return

        value = args[0]

        if name in params:
            if isinstance(params[name], str):
                params[name] = str(value)
            else:
                params[name] = float(value)

            print(f"{name} = {params[name]}")
            callback(params)

    def render(address, *args):
        callback(params)

    for name in params.keys():
        dispatcher.map(f"/qmat/{name}", set_param)

    dispatcher.map("/qmat/render", render)

    server = ThreadingOSCUDPServer((host, port), dispatcher)

    print(f"Listening for OSC on port {port}")
    server.serve_forever()
