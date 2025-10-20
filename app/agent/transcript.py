from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from ..schemas import ChatMessage


@dataclass(slots=True)
class Transcript:
    """대화 메시지 시퀀스를 파일 또는 stdout으로 기록."""

    messages: list[ChatMessage] = field(default_factory=list)

    def add(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def extend(self, items: Iterable[ChatMessage]) -> None:
        self.messages.extend(items)

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = "\n".join(f"[{msg.role}] {msg.content}" for msg in self.messages)
        path.write_text(payload, encoding="utf-8")
