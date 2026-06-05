"""Extract the Wahoo Bolt quarter-turn socket from the original stem-mount mesh.

The user supplied the PostMelvin "Wahoo_MTB_SocketV1 0deg - 90deg" stem mount
(`source_socket_mount.stl`) — a proven-fit Wahoo ELEMNT BOLT socket on top of a
curved, tyrap-strapped stem saddle. This script keeps just the socket disc
(the female quarter-turn the Bolt twist-locks into) and drops the saddle, so the
socket can be grafted (boolean union) onto other prints.

It crops the watertight mesh at the socket/saddle boundary, caps the cut, and
reorients the result: socket centered on the origin, opening +Z, flat bottom on
the XY plane. Outputs the print-ready STL and a (faceted) solid STEP.

Mesh cropping needs trimesh + friends, which are NOT project dependencies — run
this script through an ephemeral uv overlay (the committed outputs mean you
normally never need to):

    uv run --with trimesh --with numpy --with shapely --with rtree \
           --with networkx --with manifold3d \
           python wahoo_bolt_socket_mount/extract_socket.py

Geometry note: the source disc lies in X-Z with its axis along +Y; the socket
interface occupies Y >= CUT_Y and the saddle is below it (measured by per-Y disc
fill fraction: ~0.2 in the saddle, jumping to >0.6 at the socket floor).
"""

import os

import numpy as np
import trimesh
from build123d import Solid, export_step, import_stl
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS_Builder, TopoDS_Shell

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source_socket_mount.stl")
STL_OUT = os.path.join(HERE, "wahoo_bolt_socket_mount.stl")
STEP_OUT = os.path.join(HERE, "wahoo_bolt_socket_mount.step")

CUT_Y = 34.5                  # keep Y >= CUT_Y (socket); drop the saddle below
CX = (13.88 + 51.88) / 2      # source disc center, X
CZ = (3.0 + 41.0) / 2         # source disc center, Z


def crop_socket():
    m = trimesh.load(SRC)
    socket = m.slice_plane(
        plane_origin=[0, CUT_Y, 0], plane_normal=[0, 1, 0], cap=True
    )
    # Reorient: center the disc, rotate +Y -> +Z, drop flat bottom onto z=0.
    socket.apply_translation([-CX, -CUT_Y, -CZ])
    socket.apply_transform(
        trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    )
    socket.apply_translation([0, 0, -socket.bounds[0][2]])
    socket.export(STL_OUT)
    print(f"STL  watertight={socket.is_watertight} vol={socket.volume:.1f} "
          f"tris={len(socket.faces)} bounds={np.round(socket.bounds, 2).tolist()}")


def stl_to_step():
    # Wrap the watertight mesh as a single closed shell -> solid (faceted).
    face = import_stl(STL_OUT)
    builder = TopoDS_Builder()
    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    builder.Add(shell, face.wrapped)
    solid = Solid(BRepBuilderAPI_MakeSolid(shell).Solid())
    solid.label = "wahoo_bolt_socket_mount"
    export_step(solid, STEP_OUT)
    print(f"STEP volume={solid.volume:.1f} bytes={os.path.getsize(STEP_OUT)}")


if __name__ == "__main__":
    crop_socket()
    stl_to_step()
