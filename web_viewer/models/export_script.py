
import FreeCAD
import Mesh
import sys

try:
    # 문서 열기
    print("1. Opening document...")
    doc = FreeCAD.openDocument("/Users/shkim5/Documents/cadai/web_viewer/models/model_20251026_023624.FCStd")
    print("2. Document opened: " + doc.Name + ", Objects: " + str(len(doc.Objects)))
    
    # 모든 객체를 하나의 메시로 합치기
    shapes = []
    for obj in doc.Objects:
        print("3. Checking object: " + obj.Name + ", Type: " + obj.TypeId)
        if hasattr(obj, 'Shape'):
            shapes.append(obj.Shape)
            print("   - Shape added")
    
    print("4. Total shapes collected: " + str(len(shapes)))
    
    if shapes:
        # 복합 Shape 생성
        import Part
        print("5. Creating compound shape...")
        compound = Part.makeCompound(shapes)
        
        # 메시로 변환
        print("6. Converting to mesh...")
        mesh = doc.addObject("Mesh::Feature", "TempMesh")
        mesh.Mesh = Mesh.Mesh(compound.tessellate(0.1))
        
        # STL 내보내기
        print("7. Exporting to STL...")
        Mesh.export([mesh], "/Users/shkim5/Documents/cadai/web_viewer/models/model_20251026_023624.stl")
        print("SUCCESS: STL export complete: /Users/shkim5/Documents/cadai/web_viewer/models/model_20251026_023624.stl")
        
        FreeCAD.closeDocument(doc.Name)
        sys.exit(0)
    else:
        print("ERROR: No shapes to export")
        FreeCAD.closeDocument(doc.Name)
        sys.exit(1)
    
except Exception as e:
    print("ERROR: STL export failed: " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
