"""
Execution Service - Execute actions across integrations
"""
import re
from typing import Optional
from datetime import datetime

from app.services.voice.planner import ExecutionPlan, ExecutionStep, StepStatus
from app.services.voice.intent_engine import IntentType
from app.models.contact import Contact
from app.models.calendar_event import CalendarEvent
from app.models.note import Note
from app.models.reminder import Reminder


class ExecutionResult:
    """Result of execution."""
    
    def __init__(
        self,
        success: bool,
        data: Optional[dict] = None,
        error: Optional[str] = None,
        response_message: Optional[str] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.response_message = response_message


class ExecutionLayer:
    """Execute actions based on plans."""
    
    def __init__(self, db_session):
        """Initialize execution layer."""
        self.db = db_session
    
    async def execute_plan(
        self,
        plan: ExecutionPlan,
        user_id: str
    ) -> ExecutionResult:
        """Execute complete plan."""
        results = []
        
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            step.status = StepStatus.RUNNING
            
            # Execute step
            result = await self.execute_step(step, plan, user_id)
            
            if result.success:
                step.status = StepStatus.COMPLETED
                step.result = result.data
            else:
                step.status = StepStatus.FAILED
                step.error = result.error
                return ExecutionResult(
                    success=False,
                    error=f"Step {step.step_id} failed: {result.error}"
                )
            
            results.append(result)
        
        # Generate final response
        return self.generate_response(plan)
    
    async def execute_step(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan,
        user_id: str
    ) -> ExecutionResult:
        """Execute a single step."""
        action = step.action
        
        if action == "resolve_contact":
            return await self._resolve_contact(step, plan)
        elif action == "check_availability":
            return await self._check_availability(step, plan)
        elif action == "create_calendar_event":
            return await self._create_calendar_event(step, plan, user_id)
        elif action == "send_calendar_invite":
            return await self._send_calendar_invite(step, plan)
        elif action == "create_email_draft":
            return await self._create_email_draft(step, plan)
        elif action == "read_email_back":
            return await self._read_email_back(step, plan)
        elif action == "send_email":
            return await self._send_email(step, plan)
        elif action == "create_note":
            return await self._create_note(step, plan, user_id)
        elif action == "create_reminder":
            return await self._create_reminder(step, plan, user_id)
        else:
            return ExecutionResult(
                success=False,
                error=f"Unknown action: {action}"
            )
    
    async def _resolve_contact(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan
    ) -> ExecutionResult:
        """Resolve contact from role or name."""
        # Get person entity
        person_entity = None
        for entity in plan.intent.entities:
            if entity.type == "person":
                person_entity = entity
                break
        
        if not person_entity:
            return ExecutionResult(
                success=False,
                error="No person specified"
            )
        
        value = person_entity.value
        
        # Check if role reference
        if value.startswith("my "):
            role = value.replace("my ", "")
            
            # Search for contact with this role
            contact = self.db.query(Contact).filter(
                Contact.user_id == self.db.query.get(type(user_id)),
                Contact.relationships.any(role)
            ).first()
            
            if not contact:
                return ExecutionResult(
                    success=False,
                    error=f"No contact found with role '{role}'"
                )
            
            return ExecutionResult(
                success=True,
                data={
                    "resolved_contact": {
                        "id": str(contact.id),
                        "name": contact.name,
                        "email": contact.email,
                        "phone": contact.phone
                    }
                }
            )
        
        # Try to find by name
        contact = self.db.query(Contact).filter(
            Contact.email == value
        ).first() or self.db.query(Contact).filter(
            Contact.name.ilike(f"%{value}%")
        ).first()
        
        if not contact:
            return ExecutionResult(
                success=False,
                error=f"Contact not found: {value}"
            )
        
        return ExecutionResult(
            success=True,
            data={
                "resolved_contact": {
                    "id": str(contact.id),
                    "name": contact.name,
                    "email": contact.email,
                    "phone": contact.phone
                }
            }
        )
    
    async def _check_availability(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan
    ) -> ExecutionResult:
        """Check calendar availability."""
        # Get date/time from entities
        date = None
        time = None
        
        for entity in plan.intent.entities:
            if entity.type == "date":
                date = entity.value
            elif entity.type == "time":
                time = entity.value
        
        # Simplified availability check
        return ExecutionResult(
            success=True,
            data={
                "available": True,
                "message": "Calendar has availability"
            }
        )
    
    async def _create_calendar_event(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan,
        user_id: str
    ) -> ExecutionResult:
        """Create a calendar event."""
        from uuid import UUID
        
        # Parse entities
        title = plan.intent.original_text
        start_time = None
        end_time = None
        
        # Extract time from entities
        for entity in plan.intent.entities:
            if entity.type == "time":
                start_time = self._parse_time(entity.value)
            elif entity.type == "date":
                date_value = self._parse_date(entity.value)
                if start_time:
                    start_time = start_time.replace(
                        year=date_value.year,
                        month=date_value.month,
                        day=date_value.day
                    )
        
        if not start_time:
            start_time = datetime.now()
        
        if not end_time:
            end_time = start_time + timedelta(hours=1)
        
        # Create event
        event = CalendarEvent(
            user_id=UUID(user_id),
            title=title[:500],
            start_time=start_time,
            end_time=end_time,
            sync_status="pending"
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return ExecutionResult(
            success=True,
            data={
                "event_id": str(event.id),
                "title": event.title
            },
            response_message=f"Created event: {event.title}"
        )
    
    async def _send_calendar_invite(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan
    ) -> ExecutionResult:
        """Send calendar invite (placeholder for Gmail/Google Calendar)."""
        return ExecutionResult(
            success=True,
            data={"invite_sent": True}
        )
    
    async def _create_email_draft(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan
    ) -> ExecutionResult:
        """Create email draft."""
        # Get entities
        to = []
        subject = ""
        
        for entity in plan.intent.entities:
            if entity.type == "person" and entity.value:
                to.append(entity.value)
        
        # Extract subject from text
        subject_match = re.search(
            r"about\s+(?:the\s+)?(.+?)(?:\s+but|\s+for|$)",
            plan.intent.original_text,
            re.IGNORECASE
        )
        if subject_match:
            subject = subject_match.group(1).strip()
        else:
            subject = "No subject"
        
        return ExecutionResult(
            success=True,
            data={
                "draft": {
                    "to": to,
                    "subject": subject,
                    "body": plan.intent.original_text
                }
            }
        )
    
    async def _read_email_back(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan
    ) -> ExecutionResult:
        """Read back email for confirmation."""
        draft_data = {}
        
        # Find draft from previous step
        for step in plan.steps:
            if step.action == "create_email_draft":
                draft_data = step.result or {}
                break
        
        if not draft_data:
            return ExecutionResult(
                success=False,
                error="No draft found"
            )
        
        draft = draft_data.get("draft", {})
        
        return ExecutionResult(
            success=True,
            data=draft,
            response_message=f"To: {', '.join(draft.get('to', []))}"
                            f"Subject: {draft.get('subject', '')}"
        )
    
    async def _send_email(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan
    ) -> ExecutionResult:
        """Send email (placeholder for Gmail API)."""
        return ExecutionResult(
            success=True,
            data={"sent": True},
            response_message="Email sent successfully"
        )
    
    async def _create_note(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan,
        user_id: str
    ) -> ExecutionResult:
        """Create a note."""
        from uuid import UUID
        
        # Extract note content from text
        content = plan.intent.original_text
        
        # Clean up command parts
        content = re.sub(
            r"^(?:create|add|write|make|note)\s*",
            "",
            content,
            flags=re.IGNORECASE
        ).strip()
        
        if not content:
            content = "Untitled note"
        
        note = Note(
            user_id=UUID(user_id),
            content=content
        )
        
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return ExecutionResult(
            success=True,
            data={
                "note_id": str(note.id)
            },
            response_message=f"Created note: {content[:50]}..."
        )
    
    async def _create_reminder(
        self,
        step: ExecutionStep,
        plan: ExecutionPlan,
        user_id: str
    ) -> ExecutionResult:
        """Create a reminder."""
        from uuid import UUID
        
        # Extract reminder content
        content = plan.intent.original_text
        
        # Clean up command parts
        content = re.sub(
            r"^(?:remind|remember)\s*me\s*",
            "",
            content,
            flags=re.IGNORECASE
        ).strip()
        
        if content.startswith("to "):
            content = content[3:]
        
        reminder = Reminder(
            user_id=UUID(user_id),
            content=content
        )
        
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        
        return ExecutionResult(
            success=True,
            data={
                "reminder_id": str(reminder.id)
            },
            response_message=f"Reminder set: {content}"
        )
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string."""
        # Simplified time parsing
        import re
        
        match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_str, re.IGNORECASE)
        
        if not match:
            return datetime.now()
        
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        period = match.group(3)
        
        if period:
            if period.lower() == "pm" and hour != 12:
                hour += 12
            elif period.lower() == "am" and hour == 12:
                hour = 0
        
        return datetime.now().replace(hour=hour, minute=minute)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string."""
        from datetime import datetime, timedelta
        
        date_str = date_str.lower()
        
        if "today" in date_str:
            return datetime.now()
        elif "tomorrow" in date_str:
            return datetime.now() + timedelta(days=1)
        
        return datetime.now()
    
    def generate_response(self, plan: ExecutionPlan) -> ExecutionResult:
        """Generate final response message."""
        if plan.is_complete:
            # Get response from last step
            if plan.steps and plan.steps[-1].result:
                response = plan.steps[-1].result.get("response_message")
                if response:
                    return ExecutionResult(
                        success=True,
                        response_message=response
                    )
            
            return ExecutionResult(
                success=True,
                response_message="Done."
            )
        
        return ExecutionResult(
            success=False,
            error="Execution incomplete"
        )


from datetime import timedelta