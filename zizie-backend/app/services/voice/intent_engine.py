"""
Voice Intent Engine
Classifies voice commands into actionable intents
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class IntentType(Enum):
    """Intent types for voice commands."""
    CALENDAR_CREATE = "calendar_create"
    CALENDAR_READ = "calendar_read"
    CALENDAR_UPDATE = "calendar_update"
    CALENDAR_DELETE = "calendar_delete"
    EMAIL_READ = "email_read"
    EMAIL_DRAFT = "email_draft"
    EMAIL_SEND = "email_send"
    MESSAGE_SEND = "message_send"
    NOTE_CREATE = "note_create"
    NOTE_READ = "note_read"
    NOTE_UPDATE = "note_update"
    NOTE_DELETE = "note_delete"
    REMINDER_CREATE = "reminder_create"
    REMINDER_READ = "reminder_read"
    REMINDER_COMPLETE = "reminder_complete"
    MEETING_CREATE = "meeting_create"  # Video meeting
    MEETING_SUMMARIZE = "meeting_summarize"
    PHONE_CALL = "phone_call"
    NAVIGATION = "navigation"
    HELP = "help"
    SETTINGS = "settings"
    UNKNOWN = "unknown"


@dataclass
class ExtractedEntity:
    """Extracted entity from voice command."""
    type: str
    value: str
    confidence: float = 1.0


@dataclass
class Intent:
    """Parsed intent from voice command."""
    type: IntentType
    entities: list[ExtractedEntity]
    original_text: str
    confidence: float
    requires_clarification: bool = False
    clarification_message: Optional[str] = None


class IntentEngine:
    """Intent classification engine."""
    
    # Intent patterns (simplified - use LLM in production)
    PATTERNS = {
        IntentType.CALENDAR_CREATE: [
            r"(?:schedule|create|add).*(?:meeting|event|calendar|appointment)",
            r"(?:book|reserve).*(?:time|slot)",
            r"set up.*meeting",
            r"create.*event",
        ],
        IntentType.CALENDAR_READ: [
            r"(?:what(?:'s)?|show|get).*(?:on calendar|my schedule|events)",
            r"(?:check|see).*(?:calendar|schedule)",
            r"do i have.*meeting",
        ],
        IntentType.EMAIL_SEND: [
            r"(?:send|email).*(?:to|about)",
            r"(?:write).*(?:email|letter)",
            r"email.*about",
        ],
        IntentType.EMAIL_READ: [
            r"(?:read|check|show).*(?:email|mail|inbox)",
            r"(?:any|how many).*(?:email|unread)",
        ],
        IntentType.NOTE_CREATE: [
            r"(?:create|add|write|make).*note",
            r"(?:jot|put).*down",
            r"take.*note",
        ],
        IntentType.NOTE_READ: [
            r"(?:read|find|show).*(?:note|notes)",
            r"(?:what|where).*note",
        ],
        IntentType.REMINDER_CREATE: [
            r"(?:remind|remember).*(?:me|to)",
            r"(?:set|create).*reminder",
            r"don't forget",
        ],
        IntentType.MESSAGE_SEND: [
            r"(?:send|text|message).*(?:to)",
            r"(?:whatsapp|message).*",
        ],
        IntentType.MEETING_CREATE: [
            r"(?:start|create|set up).*(?:zoom|meet|teams|video)",
            r"(?:video|call|join).*(?:zoom|meet|teams)",
            r"(?:schedule|create).*video.*meeting",
            r"start.*google meet",
            r"start.*zoom call",
            r"start.*teams",
            r"start a.*meeting",
        ],
    }
    
    # Entity extraction patterns
    ENTITY_PATTERNS = {
        "person": [
            r"(?:to|with|from|about)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Full name
            r"(?:to|with|from|about)\s+(my\s+\w+)",  # Role like "my lawyer"
        ],
        "time": [
            r"at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
            r"at\s+(\d{1,2}(?::\d{2})?)",
        ],
        "date": [
            r"on\s+(today|tomorrow|next\s+\w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        ],
        "email": [
            r"to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        ],
        "platform": [
            r"(?:via|using|on|with)\s+(google\s*meet|zoom|microsoft\s*teams|teams)",
            r"(google\s*meet|zoom|teams|microsoft\s*teams)",
        ],
    }
    
    def __init__(self):
        """Initialize intent engine."""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns."""
        self.compiled_patterns = {}
        
        for intent_type, patterns in self.PATTERNS.items():
            self.compiled_patterns[intent_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
        
        self.compiled_entities = {}
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            self.compiled_entities[entity_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def parse(self, text: str) -> Intent:
        """Parse voice command into intent."""
        text = text.strip()
        
        # Check each pattern
        best_intent = None
        best_confidence = 0.0
        
        for intent_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    # Calculate confidence based on match position
                    confidence = 0.5 + (0.5 * (match.end() / len(text)))
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Check if clarification is needed
        requires_clarification = False
        clarification_message = None
        
        if best_intent in [IntentType.EMAIL_SEND, IntentType.MESSAGE_SEND]:
            if not any(e.type == "person" for e in entities):
                requires_clarification = True
                clarification_message = "Who do you want to send this to?"
        
        if best_intent == IntentType.CALENDAR_CREATE:
            if not any(e.type == "time" for e in entities):
                requires_clarification = True
                clarification_message = "What time would you like to schedule?"
        
        return Intent(
            type=best_intent or IntentType.UNKNOWN,
            entities=entities,
            original_text=text,
            confidence=best_confidence,
            requires_clarification=requires_clarification,
            clarification_message=clarification_message
        )
    
    def extract_entities(self, text: str) -> list[ExtractedEntity]:
        """Extract entities from text."""
        entities = []
        
        for entity_type, patterns in self.compiled_entities.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    value = match.group(1).strip()
                    entities.append(ExtractedEntity(
                        type=entity_type,
                        value=value,
                        confidence=0.8
                    ))
                    break  # Use first match
        
        # Extract date/time specifically
        entities.extend(self.extract_datetime(text))
        
        return entities
    
    def extract_datetime(self, text: str) -> list[ExtractedEntity]:
        """Extract date and time entities."""
        from datetime import datetime, timedelta
        import re
        
        entities = []
        
        # Date patterns
        date_pattern = re.compile(r'\b(today|tomorrow|next\s+(\w+))\b', re.IGNORECASE)
        match = date_pattern.search(text)
        
        if match:
            date_str = match.group(1).lower()
            if date_str == "today":
                date_value = datetime.now().date()
            elif date_str == "tomorrow":
                date_value = (datetime.now() + timedelta(days=1)).date()
            else:
                date_value = match.group(2)
            
            entities.append(ExtractedEntity(
                type="date",
                value=str(date_value),
                confidence=0.9
            ))
        
        # Time patterns
        time_pattern = re.compile(r'\bat\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', re.IGNORECASE)
        match = time_pattern.search(text)
        
        if match:
            time_str = match.group(1)
            entities.append(ExtractedEntity(
                type="time",
                value=time_str,
                confidence=0.9
            ))
        
        return entities


def get_intent_engine() -> IntentEngine:
    """Get intent engine singleton."""
    return IntentEngine()