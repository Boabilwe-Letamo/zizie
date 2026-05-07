"""
Planner Service - Execution planning with missing info handling
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable
from enum import Enum

from app.services.voice.intent_engine import Intent, IntentType


class StepStatus(Enum):
    """Status of execution step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionStep:
    """Single execution step."""
    step_id: str
    action: str
    params: dict
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class ExecutionPlan:
    """Complete execution plan for a voice command."""
    intent: Intent
    steps: list[ExecutionStep] = field(default_factory=list)
    current_step: int = 0
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return all(s.status == StepStatus.COMPLETED for s in self.steps)
    
    @property
    def is_failed(self) -> bool:
        """Check if any step failed."""
        return any(s.status == StepStatus.FAILED for s in self.steps)
    
    @property
    def current_action(self) -> Optional[ExecutionStep]:
        """Get current step."""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None


# Step factories for different intent types
STEP_FACTORIES = {
    IntentType.CALENDAR_CREATE: [
        {
            "step_id": "resolve_contact",
            "action": "resolve_contact",
            "params": {"person_field": "person"}
        },
        {
            "step_id": "check_availability",
            "action": "check_availability",
            "params": {}
        },
        {
            "step_id": "create_event",
            "action": "create_calendar_event",
            "params": {}
        },
        {
            "step_id": "send_invite",
            "action": "send_calendar_invite",
            "params": {}
        },
    ],
    IntentType.EMAIL_SEND: [
        {
            "step_id": "resolve_contact",
            "action": "resolve_contact",
            "params": {"person_field": "recipient"}
        },
        {
            "step_id": "draft_email",
            "action": "create_email_draft",
            "params": {}
        },
        {
            "step_id": "read_back",
            "action": "read_email_back",
            "params": {}
        },
        {
            "step_id": "send_email",
            "action": "send_email",
            "params": {}
        },
    ],
    IntentType.NOTE_CREATE: [
        {
            "step_id": "create_note",
            "action": "create_note",
            "params": {}
        },
    ],
    IntentType.REMINDER_CREATE: [
        {
            "step_id": "create_reminder",
            "action": "create_reminder",
            "params": {}
        },
    ],
}


class Planner:
    """Execution planner."""
    
    def __init__(self):
        """Initialize planner."""
        self.step_factories = STEP_FACTORIES
    
    def create_plan(self, intent: Intent) -> ExecutionPlan:
        """Create execution plan from intent."""
        plan = ExecutionPlan(
            intent=intent,
            requires_confirmation=False,
        )
        
        # Get step factory for intent type
        steps = self.step_factories.get(intent.type, [])
        
        # Build steps
        for step_def in steps:
            plan.steps.append(ExecutionStep(
                step_id=step_def["step_id"],
                action=step_def["action"],
                params=step_def.get("params", {})
            ))
        
        # Mark confirmation requirement
        if intent.type in [IntentType.EMAIL_SEND, IntentType.MESSAGE_SEND]:
            plan.requires_confirmation = True
            plan.confirmation_message = "Ready to send. Should I proceed?"
        
        return plan
    
    def get_missing_info(self, plan: ExecutionPlan) -> list[str]:
        """Identify missing information in plan."""
        missing = []
        
        for entity in plan.intent.entities:
            if entity.type == "person" and ("my " in entity.value):
                # Role reference that needs resolution
                missing.append(f"contact:{entity.value}")
            elif entity.type == "time" and not entity.value:
                missing.append("time")
            elif entity.type == "date" and not entity.value:
                missing.append("date")
        
        return missing
    
    def build_clarification_question(self, missing_fields: list[str]) -> str:
        """Build clarification question for missing fields."""
        questions = []
        
        for field in missing_fields:
            if field.startswith("contact:"):
                role = field.split(":")[1]
                questions.append(f"Who is {role}?")
            elif field == "time":
                questions.append("At what time?")
            elif field == "date":
                questions.append("On which date?")
        
        if questions:
            return " ".join(questions)
        return "Could you provide more details?"
    
    def check_rollbacks(self, plan: ExecutionPlan) -> list[dict]:
        """Check if rollback actions are needed."""
        rollbacks = []
        
        for step in plan.steps:
            if step.status == StepStatus.COMPLETED:
                # Add rollback action
                if step.action == "create_calendar_event":
                    rollbacks.append({
                        "action": "delete_calendar_event",
                        "params": {"event_id": step.result.get("event_id")}
                    })
                elif step.action == "create_email_draft":
                    rollbacks.append({
                        "action": "delete_email_draft",
                        "params": {"draft_id": step.result.get("draft_id")}
                    })
        
        return rollbacks


def create_plan_from_intent(intent: Intent) -> ExecutionPlan:
    """Create execution plan from intent."""
    planner = Planner()
    return planner.create_plan(intent)


def get_missing_information(plan: ExecutionPlan) -> list[str]:
    """Get missing information from plan."""
    planner = Planner()
    return planner.get_missing_info(plan)