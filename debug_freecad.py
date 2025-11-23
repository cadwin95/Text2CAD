import sys
import os

print(f"Python version: {sys.version}")
print(f"CWD: {os.getcwd()}")

try:
    import FreeCAD
    print("Success: Imported FreeCAD")
    print(f"FreeCAD Version: {FreeCAD.Version()}")
except ImportError as e:
    print(f"Error: Failed to import FreeCAD: {e}")

try:
    import Part
    print("Success: Imported Part")
except ImportError as e:
    print(f"Error: Failed to import Part: {e}")
