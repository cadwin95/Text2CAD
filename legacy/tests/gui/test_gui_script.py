
import FreeCAD

doc = FreeCAD.newDocument("TestDoc")

# 간단한 박스 추가
box = doc.addObject("Part::Box", "TestBox")
box.Length = 10
box.Width = 10
box.Height = 10

doc.recompute()
doc.saveAs("/Users/shkim5/Documents/cadai/test_gui_autoopen.FCStd")
FreeCAD.closeDocument(doc.Name)
print("✅ 테스트 문서 생성 완료")
