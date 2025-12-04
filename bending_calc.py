# bending_calc.py
import math

def calculate_bend_radius(tube_diameter, bend_angle, material_factor=2.0):
    """Calculate minimum bend radius (mm)"""
    return tube_diameter * material_factor

def calculate_tube_length(straight_length, bend_angle, bend_radius):
    """Calculate total tube length considering bend"""
    arc_length = math.radians(bend_angle) * bend_radius
    return straight_length + arc_length
