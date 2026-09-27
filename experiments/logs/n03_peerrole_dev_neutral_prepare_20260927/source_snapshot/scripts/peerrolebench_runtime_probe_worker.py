"""Public harmless runtime probe. No assertions or real secrets are included."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time


def main():
    for line in sys.stdin:
        request = json.loads(line)
        op = request["op"]
        try:
            if op == "read":
                value = len(Path(request["path"]).read_bytes())
            elif op == "write":
                value = Path(request["path"]).write_text("harmless-public-canary")
            elif op == "network":
                with socket.create_connection(("127.0.0.1", request["port"]), timeout=1):
                    value = True
            elif op == "fork":
                result = subprocess.run([sys.executable, "-I", "-c", "pass"], timeout=1)
                value = result.returncode
            elif op == "memory":
                allocation = bytearray(1024 * 1024 * 1024)
                time.sleep(5)
                value = len(allocation)
            elif op == "partial_line":
                os.write(1, b"{")
                time.sleep(15)
                value = None
            elif op == "flood":
                while True:
                    os.write(1, b"x" * 8192)
            else:
                raise ValueError("Unknown probe operation")
            response = {"ok": True, "value": value}
        except Exception as exc:
            response = {"ok": False, "error_type": type(exc).__name__}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
