"""LangChain workflow that drives a ship design report via LLM interactions."""
from __future__ import annotations

import argparse
from datetime import datetime
from typing import Dict, Iterable

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .ship_design_schema import (
    DesignPhase,
    EngineeringTask,
    ReviewGate,
    RiskRegisterEntry,
    ShipDesignProject,
    ShipDesignReport,
)


def _default_tasks() -> Dict[str, Iterable[EngineeringTask]]:
    return {
        "concept": [
            EngineeringTask(
                task_id="concept-hydrodynamics",
                description="Evaluate hull form families against resistance targets",
                discipline="Hydrodynamics",
                inputs=["Owner mission profile", "Speed-power curves"],
                outputs=["Candidate hull geometry set"],
                verification_method="Panel code comparison vs. requirements",
            ),
            EngineeringTask(
                task_id="concept-propulsion",
                description="Select propulsion configuration and estimate machinery weight",
                discipline="Machinery",
                inputs=["Owner mission profile", "Hull resistance estimates"],
                outputs=["Propulsion concept summary", "Preliminary weight estimate"],
                verification_method="Propulsive power balance and rule-of-thumb checks",
            ),
        ],
        "basic": [
            EngineeringTask(
                task_id="basic-structural",
                description="Size primary longitudinal members per class rules",
                discipline="Structures",
                inputs=["Class rule scantling tables", "Global loading cases"],
                outputs=["Scantling plan"],
                verification_method="Finite element spot checks vs. class criteria",
            ),
            EngineeringTask(
                task_id="basic-safety",
                description="Lay out fire zones and life-saving appliances",
                discipline="Safety",
                inputs=["SOLAS", "Owner accommodation plan"],
                outputs=["Safety plan", "Evacuation analysis"],
                verification_method="Code compliance matrix",
            ),
        ],
        "detail": [
            EngineeringTask(
                task_id="detail-piping",
                description="Route engine room piping with manufacturability annotations",
                discipline="Outfitting",
                inputs=["Machinery arrangement", "Vendor 3D models"],
                outputs=["Isometric drawings", "Pipe stress report"],
                verification_method="3D clash detection and stress check",
            ),
            EngineeringTask(
                task_id="detail-electrical",
                description="Complete cable tray routing and load analysis",
                discipline="Electrical",
                inputs=["Load balance", "Equipment schedules"],
                outputs=["Cable block diagrams", "Load flow analysis"],
                verification_method="Short circuit study and discrimination check",
            ),
        ],
    }


def _build_default_project(project_id: str) -> ShipDesignProject:
    tasks = _default_tasks()

    concept_phase = DesignPhase(
        phase_id="concept",
        name="개념 설계",
        objective="Owner mission을 충족하는 선형과 추진안을 정의",
        entry_criteria=["요구사항 베이스라인 승인"],
        exit_criteria=["선주 검토 통과", "선급 개념 승인"],
        deliverables=["개념 설계 보고서", "추진 대안 비교표"],
        stakeholders=["선주 대표", "Hydrodynamics 팀", "Machinery 팀"],
        tasks=list(tasks["concept"]),
        review_gate=ReviewGate(
            gate_id="G1",
            reviewers=["선주 PM", "선급 컨설턴트"],
            review_scope="사양 적합성, 성능 추정, 비용 거버넌스",
            approval_criteria="주요 성능지표 충족 및 위험 허용 수준",
        ),
    )

    basic_phase = DesignPhase(
        phase_id="basic",
        name="기본 설계",
        objective="규정 준수와 건조성 확보를 위한 구조/안전 기본안 확정",
        entry_criteria=["개념 설계 승인", "핵심 위험 완화 계획"],
        exit_criteria=["선급 기본승인 획득", "선주 성능 커브 서명"],
        deliverables=["선체 구조 스캐틀링 플랜", "안전 계획서"],
        stakeholders=["구조 팀", "안전 팀", "선급 심사관"],
        tasks=list(tasks["basic"]),
        review_gate=ReviewGate(
            gate_id="G2",
            reviewers=["선급 Hull Specialist", "조선소 대표"],
            review_scope="규정 적합성, 무게/복원성, 안전 레이아웃",
            approval_criteria="규정상 요구 사항 충족 및 위험 완화 실행",
        ),
    )

    detail_phase = DesignPhase(
        phase_id="detail",
        name="상세 설계",
        objective="제작 가능한 상세 도면과 생산 지원 데이터를 완성",
        entry_criteria=["기본 설계 승인"],
        exit_criteria=["제작 착수 승인", "모든 리뷰 액션 클로즈"],
        deliverables=["상세 도면 세트", "제조 작업 지시서"],
        stakeholders=["Outfitting 팀", "Electrical 팀", "생산 계획"],
        tasks=list(tasks["detail"]),
        review_gate=ReviewGate(
            gate_id="G3",
            reviewers=["생산 부서장", "QA 담당"],
            review_scope="제조성, 인터페이스 관리, 공정 위험",
            approval_criteria="제조 준비 완료 선언",
        ),
    )

    return ShipDesignProject(
        project_id=project_id,
        name="Green Horizon 12000",
        owner="BlueWave Shipping",
        classification_society="DNV",
        kickoff=datetime(2025, 1, 15),
        delivery=datetime(2027, 6, 30),
        phases=[concept_phase, basic_phase, detail_phase],
        risk_register=[
            RiskRegisterEntry(
                risk_id="R-01",
                category="Technical",
                likelihood="Medium",
                impact="High",
                mitigation="CFD campaign to validate hull options early",
                owner="Hydrodynamics Lead",
            ),
            RiskRegisterEntry(
                risk_id="R-02",
                category="Schedule",
                likelihood="Low",
                impact="High",
                mitigation="Align class review slots during concept phase",
                owner="Project Scheduler",
            ),
        ],
    )


def _project_context(project: ShipDesignProject) -> str:
    def _format_phase(phase: DesignPhase) -> str:
        lines = [
            f"Phase {phase.phase_id} - {phase.name}",
            f"Objective: {phase.objective}",
            f"Entry Criteria: {', '.join(phase.entry_criteria) or 'N/A'}",
            f"Exit Criteria: {', '.join(phase.exit_criteria) or 'N/A'}",
            f"Deliverables: {', '.join(phase.deliverables) or 'N/A'}",
            f"Stakeholders: {', '.join(phase.stakeholders) or 'N/A'}",
        ]
        task_lines = []
        for task in phase.tasks:
            task_lines.append(
                f"  - Task {task.task_id} ({task.discipline}): {task.description}. "
                f"Inputs: {', '.join(task.inputs)}. Outputs: {', '.join(task.outputs)}. "
                f"Verification: {task.verification_method}."
            )
        if phase.review_gate:
            gate = phase.review_gate
            lines.append(
                "Review Gate "
                f"{gate.gate_id}: reviewers {', '.join(gate.reviewers)}, scope {gate.review_scope}, "
                f"approval criteria {gate.approval_criteria}."
            )
        return "\n".join(lines + task_lines)

    risk_lines = [
        f"Risk {risk.risk_id} ({risk.category}) likelihood {risk.likelihood} impact {risk.impact}. "
        f"Mitigation: {risk.mitigation} (owner: {risk.owner})."
        for risk in project.risk_register
    ]

    parts = [
        f"Project {project.project_id}: {project.name}",
        f"Owner: {project.owner}, Class: {project.classification_society}",
        f"Schedule: kickoff {project.kickoff.date()} - delivery {project.delivery.date()}",
        "\n".join(_format_phase(phase) for phase in project.phases),
        "\n".join(risk_lines),
    ]
    return "\n\n".join(parts)


def build_chain() -> tuple[ChatPromptTemplate, PydanticOutputParser]:
    parser = PydanticOutputParser(pydantic_object=ShipDesignReport)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the lead naval architect assisting with documentation. "
                "Use the provided project context to produce a structured report "
                "that summarises each design phase, highlights actionable items, "
                "tracks risks, and notes review gate considerations. Respond in Korean."
            ),
            (
                "human",
                "프로젝트 정보:\n{project_context}\n\n"
                "다음 형식 지침을 반드시 따르세요.\n{format_instructions}"
            ),
        ]
    )
    return prompt, parser


def run_chain(project: ShipDesignProject) -> ShipDesignReport:
    prompt, parser = build_chain()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    chain = prompt | llm | parser
    return chain.invoke(
        {
            "project_context": _project_context(project),
            "format_instructions": parser.get_format_instructions(),
        }
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-id",
        default="SDP-001",
        help="Identifier for the demo project (used in the prompt)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    project = _build_default_project(args.project_id)
    report = run_chain(project)
    print(report.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
