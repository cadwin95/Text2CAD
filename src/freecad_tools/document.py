"""
FreeCAD 문서 관리 도구
문서 생성, 저장, 이미지 내보내기 등의 기능을 제공합니다.
"""

import os
from typing import Dict, Optional
from pathlib import Path

# FreeCAD 임포트
try:
    import FreeCAD
    import FreeCADGui
    FREECAD_AVAILABLE = True
    GUI_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False
    GUI_AVAILABLE = False
    FreeCAD = None
    FreeCADGui = None


def new_document(name: str = "Unnamed") -> Dict[str, any]:
    """
    새 FreeCAD 문서를 생성합니다.
    
    Args:
        name: 문서 이름 (기본값: "Unnamed")
    
    Returns:
        생성된 문서 정보 딕셔너리
    """
    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "document_name": name,
            "message": "FreeCAD가 설치되지 않아 시뮬레이션 모드로 실행됨"
        }
    
    doc = FreeCAD.newDocument(name)
    
    return {
        "success": True,
        "document_name": doc.Name,
        "label": doc.Label,
        "objects_count": len(doc.Objects)
    }


def get_active_document() -> Dict[str, any]:
    """
    현재 활성 문서 정보를 가져옵니다.
    
    Returns:
        활성 문서 정보 딕셔너리
    """
    if not FREECAD_AVAILABLE:
        return {
            "success": False,
            "message": "FreeCAD가 설치되지 않았습니다"
        }
    
    doc = FreeCAD.activeDocument()
    
    if doc is None:
        return {
            "success": False,
            "message": "활성 문서가 없습니다"
        }
    
    return {
        "success": True,
        "document_name": doc.Name,
        "label": doc.Label,
        "objects_count": len(doc.Objects),
        "objects": [obj.Name for obj in doc.Objects]
    }


def save_document(filepath: str, document_name: Optional[str] = None) -> Dict[str, any]:
    """
    FreeCAD 문서를 파일로 저장합니다.
    
    Args:
        filepath: 저장할 파일 경로 (.FCStd)
        document_name: 저장할 문서 이름 (None이면 활성 문서)
    
    Returns:
        저장 결과 딕셔너리
    """
    if not FREECAD_AVAILABLE:
        return {
            "success": True,
            "filepath": filepath,
            "message": "FreeCAD가 설치되지 않아 시뮬레이션 모드로 실행됨"
        }
    
    # 문서 가져오기
    if document_name:
        doc = FreeCAD.getDocument(document_name)
    else:
        doc = FreeCAD.activeDocument()
    
    if doc is None:
        return {
            "success": False,
            "message": "저장할 문서를 찾을 수 없습니다"
        }
    
    # 확장자 확인
    path = Path(filepath)
    if path.suffix.lower() != '.fcstd':
        filepath = str(path.with_suffix('.FCStd'))
    
    # 디렉토리 생성
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 문서 저장
    doc.saveAs(filepath)
    
    return {
        "success": True,
        "filepath": filepath,
        "document_name": doc.Name,
        "objects_count": len(doc.Objects)
    }


def export_image(
    filepath: str,
    width: int = 800,
    height: int = 600,
    document_name: Optional[str] = None
) -> Dict[str, any]:
    """
    FreeCAD 뷰포트를 이미지로 내보냅니다.
    
    Args:
        filepath: 저장할 이미지 경로 (.png, .jpg 등)
        width: 이미지 너비 (픽셀)
        height: 이미지 높이 (픽셀)
        document_name: 내보낼 문서 이름 (None이면 활성 문서)
    
    Returns:
        내보내기 결과 딕셔너리
    """
    if not FREECAD_AVAILABLE or not GUI_AVAILABLE:
        return {
            "success": False,
            "filepath": filepath,
            "message": "FreeCAD GUI가 사용 불가능합니다 (headless 모드에서는 이미지 내보내기 불가)"
        }
    
    # 문서 가져오기
    if document_name:
        doc = FreeCAD.getDocument(document_name)
    else:
        doc = FreeCAD.activeDocument()
    
    if doc is None:
        return {
            "success": False,
            "message": "내보낼 문서를 찾을 수 없습니다"
        }
    
    # 디렉토리 생성
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 활성 뷰 가져오기
    view = FreeCADGui.activeDocument().activeView()
    
    # 이미지 내보내기
    view.saveImage(filepath, width, height, 'White')
    
    return {
        "success": True,
        "filepath": filepath,
        "width": width,
        "height": height,
        "document_name": doc.Name
    }


def capture_viewport(
    output_dir: str = "./data/captures",
    prefix: str = "capture",
    width: int = 800,
    height: int = 600
) -> Dict[str, any]:
    """
    현재 뷰포트를 캡처하여 타임스탬프가 포함된 파일명으로 저장합니다.
    
    Args:
        output_dir: 출력 디렉토리
        prefix: 파일명 접두사
        width: 이미지 너비
        height: 이미지 높이
    
    Returns:
        캡처 결과 딕셔너리
    """
    from datetime import datetime
    
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    return export_image(filepath, width, height)

