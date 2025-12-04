import trimesh
import numpy as np

def load_stl_and_extract_centerline(file):
    mesh = trimesh.load(file, force='mesh')

    # bounding box centerline
    bbox = mesh.bounding_box_oriented
    center_points = bbox.sample_volume(50)

    # fake bend detection (you can improve later)
    bends = center_points[::10]

    return center_points, bends
