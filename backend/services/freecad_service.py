import subprocess
import os
import uuid
from pathlib import Path
from typing import Optional

# Optional headless PNG rendering
def render_stl_to_png(stl_path: Path, png_path: Path) -> bool:
    """
    Headless STL renderer using trimesh -> (fallback) matplotlib.
    Returns True on success.
    """
    # Try trimesh first (fast, good lighting)
    try:
        import trimesh
        scene = trimesh.load_mesh(str(stl_path))
        if scene is None:
            raise RuntimeError("trimesh.load_mesh returned None")
        png_bytes = scene.scene().save_image(resolution=(1024, 768), visible=True)
        if png_bytes:
            with open(png_path, "wb") as f:
                f.write(png_bytes)
            print("PNG rendered via trimesh")
            return True
    except Exception as e:
        print(f"Trimesh render failed: {e}")
    
    # Fallback to matplotlib (Agg backend)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        import numpy as np
        try:
            from stl import mesh as stlmesh
            m = stlmesh.Mesh.from_file(str(stl_path))
            faces = m.vectors
        except Exception as inner:
            print(f"numpy-stl load failed: {inner}")
            return False
        
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d")
        poly = Poly3DCollection(faces, alpha=0.85, facecolor=(0.45, 0.72, 1.0), edgecolor="k", linewidths=0.05)
        ax.add_collection3d(poly)
        scale = np.concatenate([m.x.flatten(), m.y.flatten(), m.z.flatten()])
        ax.auto_scale_xyz(scale, scale, scale)
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(png_path, dpi=160)
        plt.close(fig)
        print("PNG rendered via matplotlib")
        return True
    except Exception as e:
        print(f"Matplotlib render failed: {e}")
        return False

FREECAD_PATH = os.getenv("FREECAD_PATH", "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
MODELS_DIR = Path("backend/static/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class FreeCADService:
    @staticmethod
    def process_ocx(xml_content: str, generate_png: bool = False) -> dict:
        """
        Saves XML, runs FreeCAD to convert to STL (and optionally PNG), and returns file paths.
        """
        session_id = str(uuid.uuid4())
        xml_file = MODELS_DIR / f"{session_id}.xml"
        stl_file = MODELS_DIR / f"{session_id}.stl"
        png_file = MODELS_DIR / f"{session_id}.png" if generate_png else None
        xml_url = f"/static/models/{session_id}.xml"
        
        # Save XML
        with open(xml_file, "w") as f:
            f.write(xml_content)
            
        # Create runner script
        runner_script = MODELS_DIR / f"runner_{session_id}.py"
        
        png_export_code = ""
        if generate_png and png_file:
            png_export_code = f"""
    # Export PNG
    png_success = export_to_png(doc, "{png_file.absolute()}")
    if png_success:
        print("PNG_SUCCESS")
"""
        
        script_content = f"""
import sys
import os

# Add project root to path to find src module
sys.path.append("{os.getcwd()}")

from src.freecad_tools.ocx_importer import import_ocx, export_to_stl{"" if not generate_png else ", export_to_png"}

xml_path = "{xml_file.absolute()}"
stl_path = "{stl_file.absolute()}"

try:
    with open(xml_path, 'r') as f:
        xml_content = f.read()
        
    doc = import_ocx(xml_content)
    if doc:
        success = export_to_stl(doc, stl_path)
        if success:
            print("SUCCESS")
        else:
            print("FAILED: Export failed")
{png_export_code}
    else:
        print("FAILED: Import failed")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        with open(runner_script, "w") as f:
            f.write(script_content)
            
        # Run FreeCAD
        try:
            # Check if FreeCAD exists
            if not os.path.exists(FREECAD_PATH):
                print(f"⚠️ FreeCAD not found at {FREECAD_PATH}, returning XML only (simulation mode)")
                return {
                    "success": True,  # Considered success, but rendering skipped
                    "model_url": None,
                    "xml_url": xml_url,
                    "xml_content": xml_content,
                    "message": "OCX XML generated (FreeCAD not available, 3D rendering skipped)"
                }
            
            result = subprocess.run(
                [FREECAD_PATH, str(runner_script)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print("FreeCAD Output:", result.stdout)
            print("FreeCAD Error:", result.stderr)
            
            if stl_file.exists():
                response = {
                    "success": True,
                    "model_url": f"/static/models/{session_id}.stl",
                    "xml_url": xml_url,
                    "xml_content": xml_content,
                    "message": "OCX XML processed to STL"
                }
                
                # Add PNG URL if PNG was generated (FreeCAD GUI or headless fallback)
                png_generated = False
                if generate_png and png_file:
                    # If FreeCAD GUI already saved it, check file; otherwise headless render from STL
                    if png_file.exists():
                        png_generated = True
                    else:
                        png_generated = render_stl_to_png(stl_file, png_file)
                    
                    if png_generated and png_file.exists():
                        response["png_url"] = f"/static/models/{session_id}.png"
                        response["png_path"] = str(png_file.absolute())
                    else:
                        response["debug_info"] = response.get("debug_info", {})
                        response["debug_info"]["png"] = "PNG not generated (headless rendering failed)"
                    
                return response
            else:
                return {
                    "success": False, 
                    "error": "STL file not created",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "xml_content": xml_content,
                    "xml_url": xml_url
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"FreeCAD execution failed: {str(e)}",
                "model_url": None,
                "xml_url": xml_url,
                "xml_content": xml_content
            }
        finally:
            # Cleanup runner script
            if runner_script.exists():
                runner_script.unlink()
