# Zizie - Voice-First AI Executive Assistant

<p align="center">
  <img src="docs/logo.png" alt="Zizie Logo" width="200"/>
</p>

**Zizie** is a voice-first, always-on AI assistant that executes real-world actions across apps and services. It replaces a human executive assistant by handling calendar management, email composition/sending, messaging, note-taking, and meeting coordination — all through voice commands.

## Core Philosophy

> **Zizie does not assist users.**  
> **Zizie executes intent after biometric voice authentication.**

---

## Features

### Voice-First Experience
- 🗣️ Always-on wake word detection ("Hey Zizie")
- 🔊 Streaming speech-to-text
- 🎯 Real-time voice response generation
- 📱 Works without unlocking the phone

### Voice Biometric Security
- 🔐 Voice ID enrollment with calibration phrases
- 🛡️ Speaker verification before execution
- 👥 Multiple voice profiles per device
- 🔑 Permission levels based on enrolled profiles

### Execution Capabilities
- **Calendar**: Create, read, update, delete events
- **Email**: Draft, read, send emails with confirmation
- **Contacts**: Manage contacts with role assignments ("my lawyer", "my accountant")
- **Notes**: Create and search cloud-synced notes
- **Reminders**: Set reminders with snooze capability
- **Messaging**: Send messages (SMS, WhatsApp where APIs allow)

### Relationship-Aware System
- Natural role references: "my lawyer", "my accountant", "my assistant"
- Smart role-to-contact resolution
- Role assignment prompts for new contacts

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    ZIZIE SYSTEM ARCHITECTURE                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌──────────────────────┐         │
│  │   Mobile Client     │    │    Backend Services   │         │
│  │   (React Native)    │◀──▶│    (Node.js/FastAPI) │         │
│  └─────────────────────┘    └──────────────────────┘         │
│              │                         │                       │
│              │            ┌────────────┴────────────┐        │
│              │            │   Voice Pipeline        │        │
│              │            │  • Wake Word (Porcupine)│        │
│              │            │  • STT (Whisper)         │        │
│              │            │  • Intent Engine        │        │
│              │            │  • Planner             │        │
│              │            │  • TTS (ElevenLabs)    │        │
│              │            └─────────────────────────┘        │
│              │                         │                       │
│              │            ┌────────────┴────────────┐        │
│              │            │   Tool Integrations     │        │
│              │            │  • Google Calendar     │        │
│              │            │  • Gmail API          │        │
│              │            │  • WhatsApp API       │        │
│              │            │  • Notes DB           │        │
│              │            └─────────────────────────┘        │
│              │                         │                       │
│              │            ┌────────────┴────────────┐        │
│              │            │    Data Layer          │        │
│              │            │  • PostgreSQL         │        │
│              │            │  • Redis              │        │
│              │            │  • Encrypted Storage  │        │
│              │            └─────────────────────────┘        │
│              │                                                │
└──────────────┼────────────────────────────────────────────────┘
              ▼
```

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Backend Setup

```bash
cd zizie-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run database migrations (after PostgreSQL is running)
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

### Mobile App Setup

```bash
cd zizie-mobile

# Install dependencies
npm install

# Run on iOS
npm run ios

# Or run on Android
npm run android
```

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Voice
- `POST /api/v1/voice/enroll` - Start voice enrollment
- `POST /api/v1/voice/verify` - Verify voice
- `POST /api/v1/voice/session/start` - Start voice session
- `WS /api/v1/voice/stream/{session_id}` - WebSocket for streaming

### Contacts
- `GET /api/v1/contacts` - List contacts
- `POST /api/v1/contacts` - Create contact
- `GET /api/v1/contacts/resolve/{role}` - Resolve role to contact

### Calendar
- `GET /api/v1/calendar/events` - List events
- `POST /api/v1/calendar/events` - Create event

### Email
- `POST /api/v1/email/draft` - Create draft
- `POST /api/v1/email/send` - Send email

### Notes
- `GET /api/v1/notes` - List notes
- `POST /api/v1/notes` - Create note

### Reminders
- `GET /api/v1/reminders` - List reminders
- `POST /api/v1/reminders` - Create reminder

---

## Voice Commands

### Examples

| Command | Intent |
|---------|--------|
| "Hey Zizie, schedule a meeting with my lawyer tomorrow at 3pm" | CALENDAR_CREATE |
| "Send an email to John about the contract" | EMAIL_SEND |
| "Remind me to call my accountant" | REMINDER_CREATE |
| "What's on my calendar today?" | CALENDAR_READ |
| "Add a note about the meeting" | NOTE_CREATE |

### Safety Confirmation

Email sending **always requires confirmation**:
1. Zizie reads back the email
2. Asks "Send or edit?"
3. User confirms
4. Voice verified before execution

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL + Redis
- **Voice**: OpenAI Whisper, ElevenLabs TTS
- **Wake Word**: Picovoice Porcupine

### Mobile
- **Framework**: React Native
- **State**: Zustand
- **Storage**: Encrypted local storage

### Security
- **Encryption**: AES-256 at rest
- **Auth**: JWT + Voice biometrics
- **Compliance**: GDPR ready

---

## MVP Build Plan

### Phase 1: Foundation (Days 1-7)
- [x] Project setup and architecture
- [x] Database schema implementation
- [x] Auth system (JWT + OAuth)

### Phase 2: Voice Infrastructure (Days 8-14)
- [x] Voice pipeline setup
- [x] Wake word detection
- [x] Voice enrollment flow

### Phase 3: Core Features (Days 15-22)
- [x] Calendar integration (Google)
- [x] Email integration (Gmail API)
- [x] Contacts management
- [x] Notes system

### Phase 4: Polish & Testing (Days 23-30)
- [x] End-to-end testing
- [x] Security audit
- [x] Performance optimization

---

## License

MIT License - see LICENSE file for details.

---

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## Support

- Email: support@zizie.app
- Website: https://zizie.app

---

*Zizie — Your Voice-First Executive Assistant*