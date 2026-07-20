#!/usr/bin/env python3
"""Drive ITK-SNAP over the --agent-listen socket with paced beats for screen recording."""
import socket, json, time, sys

SOCK = sys.argv[1]

def call(cmd, args=None):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.connect(SOCK)
    s.sendall((json.dumps({"id": 1, "cmd": cmd, "args": args or {}}) + "\n").encode())
    b = b""
    while not b.endswith(b"\n"):
        c = s.recv(65536)
        if not c: break
        b += c
    s.close(); return json.loads(b.decode())

time.sleep(2.0)                                   # opening: show the CT
call("ping")
for z in (60, 90, 120, 90):                       # scrub through slices
    call("set_cursor", {"x": 128, "y": 128, "z": z}); time.sleep(0.7)
time.sleep(1.0)

# BEAT: agent applies the model's proposal (a real TotalSegmentator lung mask)
call("set_actor", {"actor": "agent"})
r = call("apply_seg_file", {"path": "/tmp/p2_proposal_10.nii.gz", "label": 1})
print("apply changed_voxels:", r["result"]["changed_voxels"], "actor:", r["result"]["audit"]["actor"])
time.sleep(3.5)                                   # dwell on the segmentation appearing

# BEAT: a correction commit (unarmed -> tagged human)
call("apply_box", {"x0": 118, "y0": 120, "z0": 85, "x1": 150, "y1": 150, "z1": 100, "label": 2})
a = call("get_audit")
print("correction actor:", a["result"]["actor"], "changed_voxels:", a["result"]["changed_voxels"])
time.sleep(3.0)
