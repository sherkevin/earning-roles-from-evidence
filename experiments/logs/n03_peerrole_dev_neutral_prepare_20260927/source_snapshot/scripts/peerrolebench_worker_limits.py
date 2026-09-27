"""Trusted launch shim: enforce finite resources before importing candidate code.

This file contains no expected outputs or grading logic. It is copied beside
the public worker; its hard limits cannot be raised by that process. Memory
is monitored externally because macOS rejects a portable RLIMIT_DATA cap. Seatbelt
is supplied by the pinned upstream sandbox-runtime, not implemented here.
"""
import os
import resource
import runpy
import sys


def main():
    worker, source, queue_name, consumer_name = sys.argv[1:5]
    limits = {
        resource.RLIMIT_CORE: 0,
        resource.RLIMIT_CPU: 8,
        resource.RLIMIT_FSIZE: 1024 * 1024,
        resource.RLIMIT_NOFILE: 64,
        resource.RLIMIT_NPROC: 0,
    }
    for which, bound in limits.items():
        resource.setrlimit(which, (bound, bound))
    # Do not expose the host's environment, including proxy/auth configuration.
    scratch = os.environ["PEERROLE_SCRATCH"]
    os.environ.clear()
    os.environ.update({"PATH": "/usr/bin:/bin", "LANG": "C", "TMPDIR": scratch})
    sys.argv = [worker, source, queue_name, consumer_name]
    runpy.run_path(worker, run_name="__main__")


if __name__ == "__main__":
    main()
