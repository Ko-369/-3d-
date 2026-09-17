import numpy as np, trimesh, json, sys
from pathlib import Path

MODEL_DIR = Path("public/models")
# target bboxes copied from generate_hardware_assets.py TARGET_BBOX
TARGET = {
 "case":        {"center":[0.0375,0.0,0.0],     "extents":[3.275,3.4,2.39]},
 "cooling":     {"center":[0.0,-0.0375,0.265],  "extents":[2.5,2.625,1.83]},
 "cpu":         {"center":[0.0,0.0,0.0],        "extents":[45.0,37.5,4.8]},
 "gpu":         {"center":[0.0,0.075,0.295],    "extents":[3.8,2.41,1.47]},
 "memory":      {"center":[0.0,-0.045,0.125],   "extents":[3.6,1.34,0.41]},
 "motherboard": {"center":[0.0,0.0025,0.1925],  "extents":[3.6,3.255,0.515]},
 "network":     {"center":[-0.0075,0.0,0.1737], "extents":[3.565,2.2,0.4925]},
 "power":       {"center":[0.0,0.0625,0.1075],  "extents":[3.25,2.825,2.665]},
 "storage":     {"center":[0.0,-0.0475,0.11],   "extents":[3.55,1.345,0.34]},
}

rows=[]
allok=True
for name,t in TARGET.items():
    sc = trimesh.load(str(MODEL_DIR/f"{name}.glb"))
    # dump(concatenate=True) bakes node-graph transforms into one mesh, so the
    # bbox is transform-accurate (same source of truth normalize_model used).
    mesh = sc.to_geometry() if isinstance(sc, trimesh.Scene) else sc
    bb=mesh.bounding_box
    c=np.asarray(bb.centroid); e=np.asarray(bb.extents)
    tc=np.asarray(t["center"]); te=np.asarray(t["extents"])
    c_err=float(np.max(np.abs(c-tc))); e_err=float(np.max(np.abs(e-te)))
    faces=int(len(mesh.faces))
    wt=bool(mesh.is_watertight)
    ok = c_err<0.02 and e_err<0.02 and wt
    allok = allok and ok
    rows.append((name, faces, f"{c_err:.4f}", f"{e_err:.4f}", "OK" if wt else "LEAK", "PASS" if ok else "FAIL"))

print(f"{'model':<12}{'faces':>7}{'centerErr':>11}{'extentErr':>11}{'watertight':>12}  result")
print("-"*70)
for r in rows:
    print(f"{r[0]:<12}{r[1]:>7}{r[2]:>11}{r[3]:>11}{r[4]:>12}  {r[5]}")
print("-"*70)
print("ALL PASS" if allok else "SOME FAILED")
sys.exit(0 if allok else 1)
