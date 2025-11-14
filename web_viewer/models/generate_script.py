
import FreeCAD
import Part

doc = FreeCAD.newDocument("WebModel")


box = doc.addObject("Part::Box", "Box")
box.Length = 10
box.Width = 10
box.Height = 10
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "DeskTop")
box.Length = 80
box.Width = 40
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "CentralLeg")
box.Length = 2
box.Width = 2
box.Height = 20
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "Leg_FL")
box.Length = 2
box.Width = 2
box.Height = 20
box.Placement.Base = FreeCAD.Vector(39, 19, 0)

box = doc.addObject("Part::Box", "Leg_FR")
box.Length = 2
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(39, -19, 0)

box = doc.addObject("Part::Box", "BasePlate")
box.Length = 10
box.Width = 10
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

doc.recompute()
doc.saveAs("/Users/shkim5/Documents/cadai/web_viewer/models/model_20251029_162859.FCStd")
FreeCAD.closeDocument(doc.Name)

# 명시적으로 종료 (인터랙티브 모드 진입 방지)
import sys
sys.exit(0)
