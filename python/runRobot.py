import sys
import js
import micropip
import json
import os
import traceback

from importlib import import_module, reload
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(""))))


class Listener:

    ROBOT_LISTENER_API_VERSION = 2

    def _post_message(self):
        js.postMessage(json.dumps({"std_output": sys.stdout.getvalue()}))
        sys.__stdout__.truncate(0)

    def start_suite(self, name, args):
        self._post_message()

    def start_test(self, name, args):
        self._post_message()

    def start_keyword(self, name, args):
        self._post_message()

    def end_keyword(self, name, args):
        self._post_message()

    def end_test(self, name, args):
        self._post_message()

    def end_suite(self, name, args):
        self._post_message()


try:
    import robot
except ImportError:
    js.postMessage(json.dumps({"std_output": "Install Robot Framework Stack Trace\n"}))
    js.postMessage(json.dumps({"std_output": f"Install Robot Framework"}))
    await micropip.install("robotframework-stacktrace")
    import robot

    js.postMessage(json.dumps({"std_output": f" = version {robot.__version__}\n"}))

try:

    def write_file(file):
        with open(file.fileName, "w") as f:
            f.writelines(file.content)

    file_list = json.loads(file_catalog)

    for file in file_list:
        write_file(file)

    try:
        js.postMessage(json.dumps({"std_output": "\n-- Running Robot Framework --\n"}))
        js.postMessage(
            json.dumps(
                {
                    "std_output": f"> robot --loglevel TRACE:INFO --exclude EXCL --skip SKIP\n"
                    f"  --removekeywords tag:REMOVE --flattenkeywords tag:FLAT test.robot\n"
                }
            )
        )
        org_stdout = sys.__stdout__
        org_stderr = sys.__stderr__
        sys.stdout = sys.__stdout__ = StringIO()
        sys.stderr = sys.__stderr__ = sys.__stdout__
        for file in file_list:
            file_name, file_ext = os.path.splitext(file.fileName)  # TODO: does not work correctly
            if file_ext == ".py":
                js.console.log(f'reimporting: {file.fileName}')
                m = import_module(file_name)
                m = reload(m)

        result = robot.run(
            "test.robot",
            consolecolors="ansi",
            listener=["RobotStackTracer", Listener()],
            loglevel="TRACE:INFO",
            # include="INCL",
            exclude="EXCL",
            skip="SKIP",
            removekeywords="tag:REMOVE",
            flattenkeywords="tag:FLAT",
        )
        js.console.log(f"result: {result}")
    except Exception as e:
        js.console.log(f"exception: {e}")
        traceback.print_exc(file=sys.__stdout__)
    finally:
        std_output = sys.__stdout__.getvalue()
        sys.__stdout__ = org_stdout
        sys.stdout = sys.__stdout__

    with open("log.html", "r") as f:
        html = str(f.read())
        js.postMessage(
            json.dumps({"html": html, "std_output": std_output, "finished": True})
        )

except Exception as e:
    print("Exception:")
    traceback.print_exc()
    print(e)
