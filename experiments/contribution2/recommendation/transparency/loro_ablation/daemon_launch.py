#!/usr/bin/env python3
"""Daemonize a shell script via double-fork + setsid (macOS has no `setsid`).

The resulting process is reparented to init, in its own session and process
group, so it is immune to SIGHUP and to the parent Bash call's process-group
teardown — it survives turn/session boundaries. Usage:
    python daemon_launch.py <script.sh> <logfile>
The invoking command returns immediately.
"""
import os
import sys
import subprocess

script, logfile = sys.argv[1], sys.argv[2]

# First fork: parent returns to caller immediately.
if os.fork() != 0:
    print(f"daemon launched (script={script})")
    sys.exit(0)
os.setsid()                      # new session + process group (escape the kill group)
if os.fork() != 0:               # second fork: prevent re-acquiring a controlling tty
    os._exit(0)

with open(logfile, "a") as f:
    f.write("\n[daemon] starting via double-fork+setsid\n")
    f.flush()
    rc = subprocess.run(
        ["/bin/bash", script],
        stdout=f, stderr=f, stdin=subprocess.DEVNULL,
        cwd="/Users/zhaoqianxue/Desktop/UPenn/PennPRS_Agent",
    ).returncode
    f.write(f"[daemon] script exited rc={rc}\n")
os._exit(0)
