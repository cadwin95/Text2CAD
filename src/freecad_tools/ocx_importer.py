import FreeCAD
import Part
import xml.etree.ElementTree as ET
import sys
import os

def import_ocx(xml_content, doc_name="OCX_Model"):
    """
    Parses OCX XML and creates FreeCAD objects.
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

    doc = FreeCAD.newDocument(doc_name)
    panel_objects = {}
    panel_meta = {}

    for vessel in root.findall(".//Vessel"):
        vessel_name = vessel.get("name", "Vessel")
        
        for panel in vessel.findall(".//Panel"):
            panel_name = panel.get("name", "Panel")
            panel_type = panel.get("type", "Plate")
            
            # Get Geometry
            geometry = panel.find("Geometry")
            if geometry is not None:
                points = []
                for pt in geometry.findall("Point"):
                    x = float(pt.get("x", 0))
                    y = float(pt.get("y", 0))
                    z = float(pt.get("z", 0))
                    points.append(FreeCAD.Vector(x, y, z))
                
                if len(points) >= 3:
                    # Close the polygon
                    points.append(points[0])
                    
                    # Create Wire
                    wire = Part.makePolygon(points)
                    
                    # Create Face
                    face = Part.Face(wire)
                    
                    # Get Material Thickness
                    thickness = 10.0 # Default
                    material = panel.find("Material")
                    if material is not None:
                        thickness = float(material.get("thickness", 10.0))
                    
                    obj = doc.addObject("Part::Feature", panel_name)
                    try:
                        normal = face.normalAt(0.5, 0.5)
                        if normal.Length == 0:
                            normal = FreeCAD.Vector(0, 0, 1)
                        normal.normalize()
                        solid = face.extrude(normal.multiply(thickness))
                        obj.Shape = solid
                    except Exception as e:
                        print(f"Extrude failed for {panel_name}, using face only: {e}")
                        obj.Shape = face
                    obj.Label = f"{panel_name} ({panel_type}, t={thickness})"
                    panel_objects[panel_name] = obj
                    panel_meta[panel_name] = {"thickness": thickness}
                    print(f"Created Panel: {panel_name}")

            # Stiffeners
            for stiffener in panel.findall("Stiffener"):
                st_name = stiffener.get("name", f"Stiffener_{len(doc.Objects)+1}")
                profile = stiffener.get("type", "Tee")
                profile_node = stiffener.find("Profile")
                height = float(profile_node.get("height", 200)) if profile_node is not None else 200.0
                width = float(profile_node.get("width", 10)) if profile_node is not None else 10.0
                web_thk = float(profile_node.get("web_thickness", 10)) if profile_node is not None else 10.0
                flange_thk = float(profile_node.get("flange_thickness", web_thk)) if profile_node is not None else web_thk
                location = stiffener.find("Location")
                if location is None:
                    continue
                start = FreeCAD.Vector(
                    float(location.get("start_x", 0)),
                    float(location.get("start_y", 0)),
                    float(location.get("start_z", 0)),
                )
                end = FreeCAD.Vector(
                    float(location.get("end_x", 0)),
                    float(location.get("end_y", 0)),
                    float(location.get("end_z", 0)),
                )
                vec = end.sub(start)
                length = vec.Length
                if length <= 0:
                    print(f"Skipping stiffener {st_name}: zero length")
                    continue

                # Cylindrical proxy for visualization and meshing
                radius = max(width, web_thk, flange_thk) / 2.0
                if radius <= 0:
                    radius = 5.0
                cyl = Part.makeCylinder(radius, length)
                rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), vec)
                cyl.Placement = FreeCAD.Placement(start, rotation)

                st_obj = doc.addObject("Part::Feature", st_name)
                st_obj.Shape = cyl
                st_obj.Label = f"{st_name} ({profile}, r={radius:.1f}, L={length:.1f})"
                print(f"Created Stiffener: {st_name} length={length:.1f}")

            # Openings
            for hole in panel.findall("Hole"):
                hole_name = hole.get("name", f"Hole_{len(doc.Objects)+1}")
                params = hole.find("Parameters")
                position = hole.find("Position")
                if params is None or position is None:
                    continue
                width = float(params.get("width", params.get("diameter", 500)))
                height = float(params.get("height", params.get("diameter", 500)))
                px = float(position.get("x", 0))
                py = float(position.get("y", 0))
                pz = float(position.get("z", 0))
                thickness = panel_meta.get(panel_name, {}).get("thickness", 10.0)
                base = FreeCAD.Vector(px - width / 2.0, py - height / 2.0, pz - thickness / 2.0)
                box = Part.makeBox(width, height, thickness)
                box.Placement = FreeCAD.Placement(base, FreeCAD.Rotation())

                # Cut opening from panel solid if possible
                target_panel = panel_objects.get(panel_name)
                if target_panel and hasattr(target_panel, "Shape") and target_panel.Shape:
                    try:
                        target_panel.Shape = target_panel.Shape.cut(box)
                    except Exception as e:
                        print(f"Opening cut failed for {hole_name}: {e}")
                print(f"Created Opening: {hole_name} size={width:.1f}x{height:.1f}")

    doc.recompute()
    return doc

def export_to_stl(doc, output_path):
    """
    Exports the document to STL.
    """
    import Mesh
    
    objects = doc.Objects
    if not objects:
        print("No objects to export.")
        return False
        
    # Collect all shapes
    shapes = []
    for obj in objects:
        if hasattr(obj, 'Shape') and obj.Shape:
            shapes.append(obj.Shape)
            
    if not shapes:
        print("No shapes found to export.")
        return False
    
    # Create a compound shape
    import Part
    compound = Part.makeCompound(shapes)
    
    # Export using MeshPart
    import MeshPart
    mesh = MeshPart.meshFromShape(compound, LinearDeflection=0.1, AngularDeflection=0.523599)
    mesh.write(output_path)
    print(f"Exported to {output_path}")
    return True

def export_to_png(doc, output_path, width=1024, height=768):
    """
    Renders the FreeCAD document to a PNG image.
    """
    try:
        import FreeCADGui
        
        # Create a view if not already in GUI mode
        if not FreeCADGui.activeDocument():
            FreeCADGui.showMainWindow()
            FreeCADGui.activateWorkbench("PartWorkbench")
        
        # Set view to fit all objects
        FreeCADGui.activeDocument().activeView().viewAxonometric()
        FreeCADGui.activeDocument().activeView().fitAll()
        
        # Save image
        FreeCADGui.activeDocument().activeView().saveImage(output_path, width, height, 'White')
        print(f"Rendered PNG to {output_path}")
        return True
    except Exception as e:
        print(f"PNG export failed: {e}")
        # Fallback: Use headless rendering if available
        try:
            # Alternative: Export using Coin3D offscreen rendering
            print("Attempting headless PNG rendering...")
            return False  # For now, require GUI mode
        except:
            return False

if __name__ == "__main__":
    # Test execution
    sample_xml = """<OCX><Vessel><Structure><Panel name="Test"><Geometry><Point x="0" y="0" z="0"/><Point x="1000" y="0" z="0"/><Point x="1000" y="1000" z="0"/><Point x="0" y="1000" z="0"/></Geometry></Panel></Structure></Vessel></OCX>"""
    doc = import_ocx(sample_xml)
    if doc:
        export_to_stl(doc, "test.stl")
        export_to_png(doc, "test.png")
