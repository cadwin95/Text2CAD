
import FreeCAD
import Part

doc = FreeCAD.newDocument("WebModel")


box = doc.addObject("Part::Box", "Rectangle")
box.Length = 10
box.Width = 10
box.Height = 1
box.Placement.Base = FreeCAD.Vector(0, 0, 50)

box = doc.addObject("Part::Box", "Seat")
box.Length = 40
box.Width = 40
box.Height = 2
box.Placement.Base = FreeCAD.Vector(-20, -20, 0)

cylinder = doc.addObject("Part::Cylinder", "Leg1")
cylinder.Radius = 2
cylinder.Height = 40
cylinder.Placement.Base = FreeCAD.Vector(-40, -40, -40)

cylinder = doc.addObject("Part::Cylinder", "Leg2")
cylinder.Radius = 2
cylinder.Height = 40
cylinder.Placement.Base = FreeCAD.Vector(-40, 0, -40)

cylinder = doc.addObject("Part::Cylinder", "Leg3")
cylinder.Radius = 2
cylinder.Height = 40
cylinder.Placement.Base = FreeCAD.Vector(0, -40, -40)

box = doc.addObject("Part::Box", "Backrest")
box.Length = 40
box.Width = 2
box.Height = 30
box.Placement.Base = FreeCAD.Vector(-20, 20, 2)

box = doc.addObject("Part::Box", "Domino")
box.Length = 15
box.Width = 4.5
box.Height = 2.5
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

cylinder = doc.addObject("Part::Cylinder", "QuestionStem")
cylinder.Radius = 1
cylinder.Height = 5
cylinder.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "Line1")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "Line2")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 2, 0)

box = doc.addObject("Part::Box", "Line3")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 4, 0)

box = doc.addObject("Part::Box", "Line4")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 6, 0)

box = doc.addObject("Part::Box", "Line5")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 8, 0)

box = doc.addObject("Part::Box", "Line6")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 10, 0)

box = doc.addObject("Part::Box", "Line7")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 12, 0)

box = doc.addObject("Part::Box", "Line8")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 14, 0)

box = doc.addObject("Part::Box", "Line9")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 16, 0)

box = doc.addObject("Part::Box", "Line10")
box.Length = 20
box.Width = 0.5
box.Height = 0.5
box.Placement.Base = FreeCAD.Vector(0, 18, 0)

box = doc.addObject("Part::Box", "L_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(1, 10, 0)

box = doc.addObject("Part::Box", "L_Horizontal")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(1, 10, 0)

box = doc.addObject("Part::Box", "L_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "L_Vertical_2")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(30, 30, 0)

box = doc.addObject("Part::Box", "L_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "L_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "LShape_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "L_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

box = doc.addObject("Part::Box", "L_Vertical")
box.Length = 20
box.Width = 2
box.Height = 2
box.Placement.Base = FreeCAD.Vector(0, 0, 0)

doc.recompute()
doc.saveAs("/Users/shkim5/Documents/cadai/web_viewer/models/model_20251026_023624.FCStd")
FreeCAD.closeDocument(doc.Name)

# 명시적으로 종료 (인터랙티브 모드 진입 방지)
import sys
sys.exit(0)
