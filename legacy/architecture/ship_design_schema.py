"""Pydantic models describing the ship design workflow."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EngineeringTask(BaseModel):
    """Concrete piece of engineering work executed within a design phase."""

    task_id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Short summary of the task")
    discipline: str = Field(..., description="Responsible engineering discipline")
    inputs: List[str] = Field(default_factory=list, description="Key inputs consumed by the task")
    outputs: List[str] = Field(default_factory=list, description="Deliverables produced by the task")
    verification_method: str = Field(
        ..., description="Method used to verify that the task output meets requirements"
    )


class RiskRegisterEntry(BaseModel):
    """Risk identified during the design process."""

    risk_id: str = Field(..., description="Unique risk identifier")
    category: str = Field(..., description="Risk category, e.g. Technical, Schedule, Cost")
    likelihood: str = Field(..., description="Qualitative likelihood assessment")
    impact: str = Field(..., description="Qualitative impact assessment")
    mitigation: str = Field(..., description="Mitigation or contingency plan")
    owner: str = Field(..., description="Responsible risk owner")


class ReviewGate(BaseModel):
    """Formal review milestone controlling progression between design phases."""

    gate_id: str = Field(..., description="Identifier for the review gate")
    reviewers: List[str] = Field(default_factory=list, description="Participants in the review")
    review_scope: str = Field(..., description="Topics evaluated by the gate")
    approval_criteria: str = Field(..., description="Conditions required to pass the gate")


class DesignPhase(BaseModel):
    """Single phase in the ship design lifecycle."""

    phase_id: str = Field(..., description="Unique identifier for the phase")
    name: str = Field(..., description="Human-readable phase name")
    objective: str = Field(..., description="Goal of the phase")
    entry_criteria: List[str] = Field(
        default_factory=list, description="Prerequisites before the phase can start"
    )
    exit_criteria: List[str] = Field(
        default_factory=list, description="Conditions required before moving forward"
    )
    deliverables: List[str] = Field(default_factory=list, description="Artifacts produced in the phase")
    stakeholders: List[str] = Field(default_factory=list, description="Stakeholders participating in the phase")
    tasks: List[EngineeringTask] = Field(default_factory=list, description="Tasks orchestrated within the phase")
    review_gate: Optional[ReviewGate] = Field(
        default=None, description="Gate performed at the end of the phase"
    )


class ShipDesignProject(BaseModel):
    """Overall container for a ship design program."""

    project_id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    owner: str = Field(..., description="Client or ship owner")
    classification_society: str = Field(..., description="Relevant classification society")
    kickoff: datetime = Field(..., description="Kickoff date")
    delivery: datetime = Field(..., description="Planned delivery date")
    phases: List[DesignPhase] = Field(default_factory=list, description="Phases included in the project")
    risk_register: List[RiskRegisterEntry] = Field(default_factory=list, description="Aggregated project risks")


class ShipDesignReportSection(BaseModel):
    """Section of a language-model generated design report."""

    phase_id: str = Field(..., description="Phase this section refers to")
    narrative: str = Field(..., description="LLM-generated narrative summary")
    recommended_actions: List[str] = Field(
        default_factory=list, description="Action items proposed by the LLM"
    )


class ShipDesignReport(BaseModel):
    """Structured report capturing LLM guidance across the workflow."""

    project_id: str = Field(..., description="Project reference")
    executive_summary: str = Field(..., description="High level summary produced by the LLM")
    sections: List[ShipDesignReportSection] = Field(
        default_factory=list, description="Per-phase guidance"
    )
    risks_to_watch: List[str] = Field(default_factory=list, description="Prioritized risk reminders")
    review_notes: List[str] = Field(default_factory=list, description="Actionable notes for review gates")
