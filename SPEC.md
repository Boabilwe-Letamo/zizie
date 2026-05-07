# Zizie - Voice-First AI Executive Assistant

## System Specification Document

**Version:** 1.0  
**Date:** 2026-05-07  
**Architect:** AI Systems Engineer  
**Status:** Production Specification

---

## 1. Executive Summary

Zizie is a voice-first AI executive assistant that executes real-world actions across apps and services. It operates fully via voice, activates via wake word "Hey Zizie", and replaces a human executive assistant by handling calendar management, email composition/sending, messaging, note-taking, and meeting coordination.

**Core Philosophy:** Zizie does not assist users—Zizie executes intent after biometric voice authentication.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ZIZIE SYSTEM ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     MOBILE CLIENT LAYER                               │   │
│  │  ┌─────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────────┐          │   │
│  │  │  iOS    │  │ React Native│  │ Android │  │  Web SDK   │          │   │
│  │  │  App    │  │   Bridge    │  │   App    │  │  (Future) │          │   │
│  │  └────┬────┘  └──────┬─────┘  └───┬────┘  └─────┬─────┘          │   │
│  └───────┼──────────────┼───────────┼────────────┼──────────────────┘   │
│          │              │           │            │                       │
│          │        ┌─────┴────┐     │       ┌────┴────┐                │
│          │        │WebSocket │      │       │   REST  │                │
│          │        │Streaming│      │       │   API   │                │
│          │        └────┬────┘      │       └────┬────┘                │
└──────────┼─────────────┼───────────┼────────────┼──────────────────────┘
           │             │           │            │
           │      ┌──────┴────┐      │      ┌──────┴───────┐
           │      │ Voice     │      │      │  Auth &     │
           │      │ Pipeline  │      │      │  Session    │
           │      │ Service   │      │      │  Gateway    │
           │      └─────┬─────┘      │      └──────┬───────┘
           │            │            │             │
┌──────────┼────────────┼────────────┼────────────┼──────────────────────────┐
│          │       ┌────┴────┐      │      ┌────┴─────┐   │                     │
│          │       │  STT     │      │      │ Identity │   │                     │
│          │       │ Engine  │      │      │ Service  │   │                     │
│          │       │(Whisper)│      │      │ (VoiceID)│   │                     │
│          │       └────┬────┘      │      └────┬────┘   │                     │
│          │            │            │           │        │                     │
│  ┌───────┴───────────┴───────────┴───────────┴────────┴─────────────────────┤  │
│  │                        BACKEND SERVICES LAYER                            │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │  │
│  │  │ Intent Engine │  │  Planner/LLMOps│  │ Execution Layer│            │  │
│  │  │ (Classification)│ │  (Orchestrator) │  │ (Tool Router)  │            │  │
│  │  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘            │  │
│  │          │                  │                   │                      │  │
│  │  ┌──────┴──────────────────┴───────────────────┴────────────────────┐ │
│  │  │                     TOOL INTEGRATION LAYER                         │ │
│  │  │  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐            │ │
│  │  │Calendar  │  │   Email    │  │ Messaging │  │  Notes    │            │ │
│  │  │Google API│  │  Gmail API │  │ WhatsApp │  │  CloudDB  │            │ │
│  │  └─────────┘  └───────────┘  └──────────┘  └───────────┘            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    DATA & PERSISTENCE LAYER                           │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │  │
│  │  │   PostgreSQL    │  │    Redis        │  │    S3/Blob       │     │  │
│  │  │  (User Data)    │  │  (Sessions)     │  │  (Voice Prints)  │     │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Voice-First Architecture

### 3.1 Voice Pipeline Components

```
┌─────────────────────────────────────────────────────────────┐
│                  VOICE PROCESSING PIPELINE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐  │
│  │  Micro   │───▶│   VAD    │───▶│   STT    │───▶│ NLU   │  │
│  │  Input   │    │(Voice    │    │(Whisper  │    │(Intent│  │
│  │  Buffer  │    │ Activity │    │  API)    │    │ Parse)│  │
│  │          │    │ Detector │    │          │    │       │  │
│  └──────────┘    └──────────┘    └──────────┘    └───────┘  │
│       ▲                                                    │  │
│       │                                                    ▼  │
│  ┌──────────┐                                        ┌──────┐│
│  │  Speaker │                                        │ TTS  ││
│  │  Verify  │◀── Response ◀─── Response ◀─────────  │(Eleven  │
│  │(Biometric│                                        │ Labs)  │
│  │ VoiceID) │                                        └──────┘│
│  └──────────┘                                              │
│       │                                                    │
│       ▼                                                    │
│  ┌──────────────────────────────────────────────┐         │
│  │                   LAYER FLOW                   │         │
│  │  1. Wake Word Detection ("Hey Zizie")         │         │
│  │  2. Audio Streaming Start                      │         │
│  │  3. Real-time STT                             │         │
│  │  4. Speaker Verification (VoiceID)            │         │
│  │  5. Intent Classification                     │         │
│  │  6. Execution Planning                        │         │
│  │  7. Action Execution                          │         │
│  │  8. Voice Response Generation                 │         │
│  └──────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Wake Word Detection

- **Engine:** Porcupine (Picovoice) - lightweight, always-on
- **Keyword:** "Hey Zizie" (custom trained)
- **Processing:** Edge-based for minimal latency
- **False Accept Rate:** < 1%
- **False Reject Rate:** < 3%

### 3.3 Speech-to-Text (STT)

- **Primary:** OpenAI Whisper API (cloud)
- **Fallback:** Whisper.cpp (on-device for offline)
- **Latency Target:** < 500ms for streaming
- **Languages:** English (initial), multilingual expansion

### 3.4 Text-to-Speech (TTS)

- **Primary:** ElevenLabs API
- **Fallback:** Google Cloud TTS
- **Voice:** Custom voice clone per user (future)
- **Latency Target:** < 300ms
- **Voice Cues:** Professional, concise responses

---

## 4. Identity & Permission System

### 4.1 Voice Biometric Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              VOICE IDENTITY SYSTEM (VIS)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                   ENROLLMENT FLOW                     │   │
│  │  1. User initiates enrollment                         │   │
│  │  2. System prompts calibration phrases                │   │
│  │  3. User speaks phrases (5-10 samples)               │   │
│  │  4. System generates voice embedding                │   │
│  │  5. Voice prints encrypted & stored                  │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                 VERIFICATION FLOW                    │   │
│  │  1. Wake word detected                                │   │
│  │  2. Audio capture for verification                  │   │
│  │  3. Real-time voice embedding extraction            │   │
│  │  4. Compare against enrolled profiles                │   │
│  │  5. Return confidence score                         │   │
│  │  6. If score > threshold → allow execution          │   │
│  │  7. If score < threshold → require PIN/fallback     │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                 CALIBRATION PHRASES                   │   │
│  │  • "Hey Zizie, schedule my day"                       │   │
│  │  • "Send an email to my lawyer about the contract" │   │
│  │  • "Remind me to call my accountant tomorrow"      │   │
│  │  • "Add a note about the meeting"                    │   │
│  │  • "What's on my calendar for tomorrow"           │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Permission Levels

| Level | Name | Description | Commands Allowed |
|-------|------|-------------|------------------|
| 0 | Guest | Unauthenticated | None - wake word only |
| 1 | Basic | Voice-verified basic | Read calendar, read emails, read notes |
| 2 | Standard | Full voice access | All read + compose, send messages, create events |
| 3 | Admin | Full access | All actions including account changes |
| 4 | Owner | Device owner | Unlimited, can manage other profiles |

### 4.3 Voice Profile Database Schema

```sql
-- voice_profiles table
CREATE TABLE voice_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    profile_name VARCHAR(100) NOT NULL,
    permission_level INTEGER DEFAULT 1,
    -- Voice embedding stored as vector (1536 dims for Whisper)
    voice_embedding BYTEA NOT NULL,
    -- Salt for additional security
    embedding_salt VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    -- Enrollment status
    enrollment_complete BOOLEAN DEFAULT FALSE,
    enrollment_samples INTEGER DEFAULT 0
);

-- Voice prints are encrypted at rest using AES-256
-- Additional LUKS full-disk encryption on storage volume
```

---

## 5. Relationship-Aware Contact System

### 5.1 Contact & Role Mapping

```
┌─────────────────────────────────────────────────────────────┐
│              RELATIONSHIP MANAGEMENT SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USER UTTERANCE: "Send email to my lawyer"                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              RESOLUTION PIPELINE                      │   │
│  │                                                      │   │
│  │  "my lawyer"                                         │   │
│  │       │                                              │   │
│  │       ▼                                              │   │
│  │  ──────────────────────────────────────             │   │
│  │  Check contacts.relationship_map                    │   │
│  │  WHERE user_id = ? AND role = 'lawyer'              │   │
│  │       │                                              │   │
│  │       ▼ (found)                                     │   │
│  │  ──────────────────────────────────────             │   │
│  │  Resolve: John Smith (john@lawfirm.com)              │   │
│  │       │                                              │   │
│  │       ▼ (not found - prompt)                        │   │
│  │  ──────────────────────────────────────             │   │
│  │  "I don't have a lawyer in your contacts."          │   │
│  │  "Would you like to assign a role to someone?"      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CONTACTS TABLE                         │   │
│  │                                                      │   │
│  │  contacts (                                         │   │
│  │    id UUID,                                         │   │
│  │    user_id UUID,                                    │   │
│  │    name VARCHAR(255),                                │   │
│  │    email VARCHAR(255),                               │   │
│  │    phone VARCHAR(50),                                │   │
│  │    relationships JSONB,  -- ["lawyer", "legal"]     │   │
│  │    metadata JSONB,                                   │   │
│  │    created_at TIMESTAMP                              │   │
│  │  )                                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Predefined Role Categories

| Category | Roles |
|-----------|-------|
| Professional | lawyer, accountant, doctor, therapist, financial advisor |
| Personal | spouse, partner, mother, father, sibling, friend |
| Work | boss, manager, colleague, team lead, HR, assistant |
| Service | landlord, mechanic, dentist, trainer |

---

## 6. Execution Engine Architecture

### 6.1 Multi-Layer Processing

```
┌─────────────────────────────────────────────────────────────┐
│                 EXECUTION ENGINE LAYERS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LAYER 1: VOICE INTERFACE                             │   │
│  │  • Wake word detection (always-on)                  │   │
│  │  • Audio stream management                           │   │
│  │  • Voice session management                          │   │
│  │  • Push-to-talk fallback                            │   │
│  └───────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LAYER 2: INTENT ENGINE                              │   │
│  │  • Command classification                           │   │
│  │  • Entity extraction (people, time, context)        │   │
│  │  • Confidence scoring                                │   │
│  │  • Ambiguity detection                               │   │
│  │                                                      │   │
│  │  Intent Types:                                        │   │
│  │  • CALENDAR: create, read, update, delete            │   │
│  │  • EMAIL: read, draft, send, reply                  │   │
│  │  • MESSAGE: send, read                               │   │
│  │  • NOTE: create, read, update, search                │   │
│  │  • REMINDER: set, list, complete                     │   │
│  │  • MEETING: summarize, extract action items         │   │
│  │  • PHONE: call, dial                                │   │
│  │  • NAVIGATION: directions, location                 │   │
│  └───────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LAYER 3: PLANNER                                      │   │
│  │  • Break request into steps                          │   │
│  │  • Handle missing information                        │   │
│  │  • Build execution graph                             │   │
│  │  • Handle dependencies                             │   │
│  │  • Plan rollback strategies                        │   │
│  │                                                      │   │
│  │  Example: "Schedule meeting with Thabo tomorrow"     │   │
│  │  ─────────────────────────────────────────────        │   │
│  │  Step 1: Find contact "Thabo"                       │   │
│  │  Step 2: Get tomorrow date                          │   │
│  │  Step 3: Check calendar availability                │   │
│  │  Step 4: Create calendar event                      │   │
│  │  Step 5: Send invitation to Thabo                  │   │
│  │  Step 6: Confirm to user                            │   │
│  └───────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LAYER 4: TOOL ROUTER                                 │   │
│  │  • Route to correct API/service                     │   │
│  │  • Load appropriate credentials                    │   │
│  │  • Format request according to API                 │   │
│  │  • Handle rate limiting                             │   │
│  │  • Circuit breaker pattern                         │   │
│  └───────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LAYER 5: EXECUTION LAYER                             │   │
│  │  • Execute actions atomically                       │   │
│  │  • Transaction management                          │   │
│  │  • Rollback on failure                              │   │
│  │  • Confirmation for sensitive actions             │   │
│  │  • Audit logging                                    │   │
│  └───────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LAYER 6: VOICE RESPONSE                              │   │
│  │  • Generate concise response                         │   │
│  │  • TTS conversion                                   │   │
│  │  • Confirmation for sensitive actions              │   │
│  │  • Error reporting                                  │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Intent Classification Examples

| User Input | Intent | Entities | Confidence |
|-----------|--------|-----------|-------------|
| "Hey Zizie, schedule meeting with my lawyer tomorrow at 3pm" | CALENDAR_CREATE | {"person": "lawyer", "date": "tomorrow", "time": "3pm"} | 0.95 |
| "Send email to John about the contract" | EMAIL_SEND | {"recipient": "john", "subject": "contract"} | 0.88 |
| "Remind me to call my accountant" | REMINDER_CREATE | {"action": "call accountant", "when": "tomorrow"} | 0.82 |
| "What's on my calendar today?" | CALENDAR_READ | {"date": "today"} | 0.99 |
| "Add note about the meeting" | NOTE_CREATE | {"content": "meeting notes"} | 0.75 |

---

## 7. API Endpoints

### 7.1 Authentication & Identity

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/auth/register` | POST | Register new user | No |
| `/api/v1/auth/login` | POST | User login | No |
| `/api/v1/voice/enroll` | POST | Start voice enrollment | User |
| `/api/v1/voice/enroll/complete` | POST | Complete enrollment | User |
| `/api/v1/voice/verify` | POST | Verify voice (for command) | User |
| `/api/v1/voice/profiles` | GET | List voice profiles | User |
| `/api/v1/voice/profiles/:id` | DELETE | Delete voice profile | User |

### 7.2 Voice Session

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/voice/session/start` | POST | Start voice session | User |
| `/api/v1/voice/session/end` | POST | End voice session | User |
| `/api/v1/voice/stream` | WS | WebSocket streaming | User |
| `/api/v1/voice/command` | POST | Submit voice command | User |

### 7.3 Contacts

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/contacts` | GET | List contacts | User |
| `/api/v1/contacts` | POST | Add contact | User |
| `/api/v1/contacts/:id` | PUT | Update contact | User |
| `/api/v1/contacts/:id` | DELETE | Delete contact | User |
| `/api/v1/contacts/resolve/:role` | GET | Resolve role to contact | User |
| `/api/v1/contacts/:id/assign-role` | POST | Assign role to contact | User |

### 7.4 Calendar

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/calendar/events` | GET | List events | User |
| `/api/v1/calendar/events` | POST | Create event | User |
| `/api/v1/calendar/events/:id` | PUT | Update event | User |
| `/api/v1/calendar/events/:id` | DELETE | Delete event | User |
| `/api/v1/calendar/availability` | GET | Check availability | User |

### 7.5 Email

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/email/messages` | GET | List messages | User |
| `/api/v1/email/messages/:id` | GET | Get message | User |
| `/api/v1/email/draft` | POST | Create draft | User |
| `/api/v1/email/send` | POST | Send email | User + Confirm |
| `/api/v1/email/draft/:id` | PUT | Update draft | User |
| `/api/v1/email/draft/:id` | DELETE | Delete draft | User |

### 7.6 Notes

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/notes` | GET | List notes | User |
| `/api/v1/notes` | POST | Create note | User |
| `/api/v1/notes/:id` | PUT | Update note | User |
| `/api/v1/notes/:id` | DELETE | Delete note | User |
| `/api/v1/notes/search` | GET | Search notes | User |

### 7.7 Reminders

| Endpoint | Method | Description | Auth Required |
|---------|--------|-------------|---------------|
| `/api/v1/reminders` | GET | List reminders | User |
| `/api/v1/reminders` | POST | Create reminder | User |
| `/api/v1/reminders/:id` | PUT | Update reminder | User |
| `/api/v1/reminders/:id` | DELETE | Delete reminder | User |
| `/api/v1/reminders/:id/complete` | POST | Complete reminder | User |

---

## 8. Database Schema

### 8.1 Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    -- Language preference
    language VARCHAR(10) DEFAULT 'en',
    -- Device identifier
    device_id VARCHAR(255),
    -- OAuth providers
    providers JSONB DEFAULT '{}',
    -- Settings
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

-- Contacts table with relationship mapping
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    -- Role relationships: lawyer, assistant, etc.
    relationships JSONB DEFAULT '[]',
    -- Additional metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, email)
);

-- Calendar events
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(500),
    attendees JSONB DEFAULT '[]',
    -- External calendar ID (Google Calendar)
    external_id VARCHAR(255),
    -- Sync status
    sync_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notes
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500),
    content TEXT NOT NULL,
    -- Tags for organization
    tags JSONB DEFAULT '[]',
    -- Linked entities
    linked_entities JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Reminders
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    content VARCHAR(1000) NOT NULL,
    due_time TIMESTAMP,
    -- Associated entity (contact, event, note)
    entity_type VARCHAR(50),
    entity_id UUID,
    status VARCHAR(50) DEFAULT 'pending',
    -- Completion info
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Voice sessions for audit
CREATE TABLE voice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    profile_id UUID REFERENCES voice_profiles(id),
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    -- Session metadata
    commands_count INTEGER DEFAULT 0,
    commands JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active'
);

-- Action audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID REFERENCES voice_sessions(id),
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB DEFAULT '{}',
    result VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 9. Safety & Confirmation Rules

### 9.1 Confirmation Requirements

| Action | Low Risk | Medium Risk | High Risk |
|--------|----------|-------------|------------|
| Read calendar | Auto-execute | - | - |
| Read email | Auto-execute | - | - |
| Create calendar event | Auto-execute | Voice confirm | - |
| Send email | Read back + Confirm | PIN confirmation | Block |
| Send message | Voice confirm | PIN confirmation | Block |
| Delete data | Confirm | Double confirm | Block |
| Account changes | - | PIN confirmation | Block + 2FA |

### 9.2 Confirmation Flow for Email

```
┌─────────────────────────────────────────────────────────────┐
│                  EMAIL SENDING FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User: "Send email to John about the contract"              │
│                                                              │
│  Step 1: Draft email                                        │
│  Zizie: "Here's the draft: To: John" (reads body)           │
│          "Subject: Contract"                                 │
│          "Shall I send or edit?"                            │
│                                                              │
│  User: "Send"                                               │
│                                                              │
│  Step 2: Voice verify                                       │
│  [Verify speaker identity]                                   │
│  ✓ Identity confirmed (confidence: 95%)                   │
│                                                              │
│  Step 3: Execute                                             │
│  [Send via Gmail API]                                        │
│  ✓ Email sent successfully                                 │
│                                                              │
│  Step 4: Confirm                                             │
│  Zizie: "Email sent to John about the contract."           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Mobile App Structure

### 10.1 React Native Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MOBILE APP STRUCTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ZizieMobile/                                                │
│  ├── src/                                                   │
│  │   ├── components/          # Reusable UI components       │
│  │   │   ├── Button.tsx                                    │
│  │   │   ├── Card.tsx                                      │
│  │   │   ├── Input.tsx                                     │
│  │   │   ├── VoiceIndicator.tsx                          │
│  │   │   └── StatusBadge.tsx                              │
│  │   ├── screens/             # Screen components             │
│  │   │   ├── HomeScreen.tsx                                │
│  │   │   ├── SettingsScreen.tsx                          │
│  │   │   ├── ContactsScreen.tsx                         │
│  │   │   ├── VoiceEnrollmentScreen.tsx                 │
│  │   │   └── CalendarScreen.tsx                          │
│  │   ├── navigation/         # Navigation config            │
│  │   │   └── AppNavigator.tsx                           │
│  │   ├── services/         # API & integration services  │
│  │   │   ├── api.ts            # REST API client           │
│  │   │   ├── voice.ts        # Voice processing           │
│  │   │   ├── auth.ts         # Authentication          │
│  │   │   └── storage.ts     # Local storage            │
│  │   ├── hooks/            # Custom React hooks        │
│  │   │   ├── useVoice.ts                                │
│  │   │   ├── useAuth.ts                                │
│  │   │   └── useContacts.ts                           │
│  │   ├── store/            # State management          │
│  │   │   └── index.tsx     # Zustand store            │
│  │   ├── utils/            # Utility functions         │
│  │   │   ├── datetime.ts                               │
│  │   │   └── validation.ts                            │
│  │   ├── types/            # TypeScript definitions     │
│  │   │   └── index.ts                                 │
│  │   └── constants/       # App constants            │
│  │       └── theme.ts                                 │
│  ├── ios/                   # iOS native code          │
│  ├── android/              # Android native code        │
│  ├── __tests__/           # Test files             │
│  └── App.tsx              # Root component         │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           KEY MOBILE FEATURES                        │   │
│  │                                                      │   │
│  │  • Wake word detection (Porcupine integration)        │   │
│  │  • Background voice processing                    │   │
│  │  • Push notification for reminders               │   │
│  │  • Offline capability for critical features   │   │
│  │  • Biometric authentication                   │   │
│  │  • Encrypted local storage                    │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Backend Service Structure

### 11.1 Node.js/FastAPI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND STRUCTURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  zizie-backend/                                              │
│  ├── app/                                                   │
│  │   ├── api/                  # API routes                  │
│  │   │   ├── v1/                                         │
│  │   │   │   ├── auth.py                                  │
│  │   │   │   ├── voice.py                              │
│  │   │   │   ├── contacts.py                          │
│  │   │   │   ├── calendar.py                         │
│  │   │   │   ├── email.py                           │
│  │   │   │   ├── notes.py                          │
│  │   │   │   └── reminders.py                       │
│  │   ├── core/                 # Core functionality       │
│  │   │   ├── config.py                                 │
│  │   │   ├── security.py                             │
│  │   │   └── exceptions.py                          │
│  │   ├── services/            # Business logic         │
│  │   │   ├── voice/                                   │
│  │   │   │   ├── intent_engine.py                    │
│  │   │   │   ├── planner.py                          │
│  │   │   │   └── execution.py                       │
│  │   │   ├── identity/                              │
│  │   │   │   └── voice_recognition.py               │
│  │   │   └── integrations/                         │
│  │   │       ├── google_calendar.py                  │
│  │   │       ├── gmail.py                           │
│  │   │       └── whatsapp.py                       │
│  │   ├── models/              # Database models        │
│  │   │   ├── user.py                                  │
│  │   │   ├── contact.py                             │
│  │   │   ├── event.py                             │
│  │   │   └── note.py                              │
│  │   ├── schemas/            # Pydantic schemas      │
│  │   │   ├── user.py                                  │
│  │   │   ├── contact.py                             │
│  │   │   └── voice.py                              │
│  │   └── db/                  # Database setup       │
│  │       ├── base.py                                 │
│  │       └── session.py                              │
│  ├── tests/                 # Test suite            │
│  ├── scripts/              # Utility scripts        │
│  ├── requirements.txt     # Python dependencies   │
│  ├── .env.example       # Environment template │
│  └── main.py             # Application entry  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           SERVICE DEPENDENCIES                        │   │
│  │                                                      │   │
│  │  Python: 3.11+                                       │   │
│  │  FastAPI: Web framework                               │   │
│  │  Pydantic: Data validation                          │   │
│  │  SQLAlchemy: ORM                                    │   │
│  │  PostgreSQL: Primary database                       │   │
│  │  Redis: Session cache                              │   │
│  │  OpenAI: Whisper & GPT                            │   │
│  │  ElevenLabs: TTS                                   │   │
│  │  Picovoice: Wake word                             │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. MVP Build Plan

### 12.1 30-Day Build Timeline

```
┌─────────────────────────────────────────────────────────────┐
│                    30-DAY MVP TIMELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PHASE 1: Foundation (Days 1-7)                            │
│  ──────────────────────────────────────                    │
│  □ Day 1-2: Project setup, architecture finalization        │
│  □ Day 3-4: Database schema implementation                │
│  □ Day 5-6: Auth system (JWT + OAuth)                      │
│  □ Day 7:   Basic API structure, testing setup             │
│                                                              │
│  PHASE 2: Voice Infrastructure (Days 8-14)                  │
│  ──────────────────────────────────────                   │
│  □ Day 8-9:  Voice pipeline setup (STT/TTS)                │
│  □ Day 10-11: Wake word detection integration              │
│  □ Day 12-13: Voice enrollment flow                      │
│  □ Day 14:   Basic intent recognition                    │
│                                                              │
│  PHASE 3: Core Features (Days 15-22)                       │
│  ──────────────────────────────────────                   │
│  □ Day 15-16: Calendar integration (Google)               │
│  □ Day 17-18: Email integration (Gmail API)               │
│  □ Day 19-20: Contacts management                       │
│  □ Day 21-22: Notes system                             │
│                                                              │
│  PHASE 4: Polish & Testing (Days 23-30)                     │
│  ──────────────────────────────────────                   │
│  □ Day 23-25: End-to-end voice flow testing              │
│  □ Day 26-27: Security audit                            │
│  □ Day 28-29: Performance optimization                  │
│  □ Day 30:  MVP release candidate                       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MVP SUCCESS CRITERIA                  │   │
│  │                                                      │   │
│  │  □ Wake word detection works reliably             │   │
│  │  □ Voice enrollment completes in <5 minutes        │   │
│  │  □ Speaker verification returns in <1 second        │   │
│  │  □ Calendar events can be created via voice          │   │
│  │  □ Emails can be drafted and sent via voice         │   │
│  │  □ Contacts can be managed via voice               │   │
│  │  □ Notes can be created and retrieved               │   │
│  │  □ Response TTS latency < 500ms                     │   │
│  │  □ 95% command recognition accuracy              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 60-Day Expanded Features

| Feature | Timeline | Priority |
|---------|----------|----------|
| Advanced intent classification | Days 31-40 | P1 |
| Reminder system | Days 31-35 | P1 |
| Message sending (SMS) | Days 36-42 | P2 |
| Meeting notes summarization | Days 36-45 | P2 |
| Multi-language support | Days 46-55 | P3 |
| Offline mode | Days 46-55 | P3 |
| WhatsApp integration | Days 50-60 | P3 |

---

## 13. Security Considerations

### 13.1 Security Requirements

- **Encryption:** AES-256 for voice prints, TLS 1.3 for transit
- **Authentication:** JWT + Voice biometrics
- **Authorization:** Role-based access control (RBAC)
- **Audit:** Full action audit logging
- **PII:** GDPR compliant data handling
- **Biometric:** On-device processing where possible

### 13.2 Threat Prevention

| Threat | Mitigation |
|--------|------------|
| Voice spoofing | Liveness detection, random challenges |
| Unauthorized access | Voice verification + PIN fallback |
| Data breach | Encryption at rest + minimum privilege |
| API abuse | Rate limiting + circuit breakers |
| Man-in-middle | TLS 1.3 + certificate pinning |

---

## 14. Success Metrics

### 14.1 Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|------------|
| Wake word accuracy | > 98% | Test suite |
| Command accuracy | > 95% | Lambda test |
| Voice enrollment time | < 5 min | UX research |
| Response latency | < 2 sec | APM metrics |
| User satisfaction | > 4.5/5 | User survey |
| Task completion | > 90% | Usage analytics |

---

*End of Specification Document*