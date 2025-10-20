from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class CreateBoxParams(BaseModel):
    """FreeCAD 박스 생성 요청 파라미터."""

    length: float = Field(..., gt=0, description="X축 길이(mm)")
    width: float = Field(..., gt=0, description="Y축 길이(mm)")
    height: float = Field(..., gt=0, description="Z축 길이(mm)")
    doc_name: str = Field(
        default="GeneratedBox",
        description="생성할 FreeCAD 문서 이름",
    )
    output_path: str | None = Field(
        default=None,
        description="저장할 FCStd 경로 (옵션)",
    )

    @field_validator("doc_name")
    @classmethod
    def _validate_doc_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("doc_name must not be empty")
        return cleaned


class CreateBoxResult(BaseModel):
    """FreeCAD 박스 생성 결과."""

    command: str = Field(default="", description="사용된 FreeCADCmd 경로")
    script: str = Field(description="실행한(또는 실행할) Python 스크립트")
    executed: bool = Field(default=False, description="실행 여부")
    returncode: int | None = Field(default=None, description="FreeCADCmd 반환 코드")
    stdout: str = Field(default="", description="표준 출력 캡쳐")
    stderr: str = Field(default="", description="표준 에러 캡쳐")
    saved_path: str | None = Field(default=None, description="저장된 FCStd 경로")


__all__ = ["CreateBoxParams", "CreateBoxResult"]
