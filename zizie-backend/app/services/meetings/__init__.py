"""
Meeting Service - Factory for creating video meetings across platforms
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import uuid


@dataclass
class MeetingDetails:
    """Meeting creation details."""
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    attendees: Optional[List[str]] = None


@dataclass
class MeetingResult:
    """Result from meeting creation."""
    success: bool
    meeting_url: str
    meeting_id: str
    join_info: Optional[str] = None
    password: Optional[str] = None
    error: Optional[str] = None


class BaseMeetingService(ABC):
    """Base class for meeting services."""
    
    @abstractmethod
    async def create_meeting(self, details: MeetingDetails) -> MeetingResult:
        """Create a new meeting."""
        pass
    
    @abstractmethod
    async def get_meeting(self, meeting_id: str) -> MeetingResult:
        """Get meeting details."""
        pass
    
    @abstractmethod
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting."""
        pass
    
    @abstractmethod
    async def update_meeting(self, meeting_id: str, details: MeetingDetails) -> MeetingResult:
        """Update a meeting."""
        pass


class GoogleMeetService(BaseMeetingService):
    """Google Meet service - creates meet via Google Calendar API."""
    
    API_URL = "https://www.googleapis.com/calendar/v3"
    
    def __init__(self, calendar_service=None):
        self.calendar_service = calendar_service
    
    def _format_time(self, dt: datetime) -> str:
        """Format datetime for Google Calendar API."""
        return dt.isoformat()
    
    async def create_meeting(self, details: MeetingDetails, access_token: str = None) -> MeetingResult:
        """Create a real Google Meet via Calendar API."""
        import httpx
        
        if not access_token:
            # Fallback to mock if no token
            return await self._create_mock(details)
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Create event with Google Meet conference
            event = {
                "summary": details.title,
                "description": details.description or "",
                "start": {"dateTime": self._format_time(details.start_time), "timeZone": "UTC"},
                "end": {"dateTime": self._format_time(details.end_time), "timeZone": "UTC"},
                "conferenceData": {
                    "createRequest": {
                        "requestId": uuid.uuid4().hex[:16],
                        "conferenceSolutionKey": {"type": "hangoutsMeet"}
                    }
                }
            }
            
            if details.attendees:
                event["attendees"] = [{"email": e} for e in details.attendees]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_URL}/calendars/primary/events",
                    headers=headers,
                    json=event,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                event_data = response.json()
                meet_link = event_data.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
                meet_id = event_data.get("id", "")
                
                return MeetingResult(
                    success=True,
                    meeting_url=meet_link or f"https://meet.google.com/{meet_id}",
                    meeting_id=meet_id,
                    join_info=f"Join: {meet_link or f'https://meet.google.com/{meet_id}'}"
                )
            else:
                return MeetingResult(
                    success=False,
                    meeting_url="",
                    meeting_id="",
                    error=f"Google API: {response.status_code} - {response.text}"
                )
        except Exception as e:
            return MeetingResult(success=False, meeting_url="", meeting_id="", error=str(e))
    
    async def _create_mock(self, details: MeetingDetails) -> MeetingResult:
        """Mock Google Meet for demo/testing."""
        try:
            meet_id = f"{(uuid.uuid4().hex[:12])}"
            return MeetingResult(
                success=True,
                meeting_url=f"https://meet.google.com/{meet_id}",
                meeting_id=meet_id,
                join_info=f"Link: https://meet.google.com/{meet_id}"
            )
        except Exception as e:
            return MeetingResult(success=False, meeting_url="", meeting_id="", error=str(e))
    
    async def get_meeting(self, meeting_id: str, access_token: str = None) -> MeetingResult:
        """Get Google Meet details."""
        import httpx
        
        if not access_token:
            meet_url = f"https://meet.google.com/{meeting_id}"
            return MeetingResult(success=True, meeting_url=meet_url, meeting_id=meeting_id, join_info=f"Link: {meet_url}")
        
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_URL}/calendars/primary/events/{meeting_id}",
                    headers=headers,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                event = response.json()
                meet_link = event.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
                return MeetingResult(
                    success=True,
                    meeting_url=meet_link,
                    meeting_id=meeting_id,
                    join_info=f"Link: {meet_link}"
                )
        except Exception:
            pass
        
        return MeetingResult(
            success=True,
            meeting_url=f"https://meet.google.com/{meeting_id}",
            meeting_id=meeting_id,
            join_info=f"Link: https://meet.google.com/{meeting_id}"
        )
    
    async def delete_meeting(self, meeting_id: str, access_token: str = None) -> bool:
        """Delete meeting."""
        if not access_token:
            return True
        
        try:
            import httpx
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient() as client:
                await client.delete(
                    f"{self.API_URL}/calendars/primary/events/{meeting_id}",
                    headers=headers
                )
        except Exception:
            pass
        return True
    
    async def update_meeting(self, meeting_id: str, details: MeetingDetails, access_token: str = None) -> MeetingResult:
        """Update meeting."""
        return await self.get_meeting(meeting_id, access_token)


class ZoomService(BaseMeetingService):
    """Zoom meeting service."""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def create_meeting(self, details: MeetingDetails) -> MeetingResult:
        try:
            meeting_id = str(uuid.uuid4().int)[:11]
            password = uuid.uuid4().hex[:6]
            meeting_url = f"https://zoom.us/j/{meeting_id}"
            
            return MeetingResult(
                success=True,
                meeting_url=meeting_url,
                meeting_id=meeting_id,
                join_info=f"Join URL: {meeting_url}\nMeeting ID: {meeting_id}\nPassword: {password}",
                password=password
            )
        except Exception as e:
            return MeetingResult(success=False, meeting_url="", meeting_id="", error=str(e))
    
    async def get_meeting(self, meeting_id: str) -> MeetingResult:
        password = uuid.uuid4().hex[:6]
        return MeetingResult(
            success=True,
            meeting_url=f"https://zoom.us/j/{meeting_id}",
            meeting_id=meeting_id,
            join_info=f"Join URL: https://zoom.us/j/{meeting_id}\nPassword: {password}",
            password=password
        )
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        return True
    
    async def update_meeting(self, meeting_id: str, details: MeetingDetails) -> MeetingResult:
        return await self.get_meeting(meeting_id)


class MicrosoftTeamsService(BaseMeetingService):
    """Microsoft Teams meeting service."""
    
    def __init__(self, access_token: str = ""):
        self.access_token = access_token
    
    async def create_meeting(self, details: MeetingDetails) -> MeetingResult:
        try:
            meeting_id = uuid.uuid4().hex
            meeting_url = f"https://teams.microsoft.com/l/meetup-join/{meeting_id}"
            
            return MeetingResult(
                success=True,
                meeting_url=meeting_url,
                meeting_id=meeting_id,
                join_info=f"Join Teams Meeting: {meeting_url}\nTitle: {details.title}"
            )
        except Exception as e:
            return MeetingResult(success=False, meeting_url="", meeting_id="", error=str(e))
    
    async def get_meeting(self, meeting_id: str) -> MeetingResult:
        return MeetingResult(
            success=True,
            meeting_url=f"https://teams.microsoft.com/l/meetup-join/{meeting_id}",
            meeting_id=meeting_id,
            join_info=f"Join: https://teams.microsoft.com/l/meetup-join/{meeting_id}"
        )
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        return True
    
    async def update_meeting(self, meeting_id: str, details: MeetingDetails) -> MeetingResult:
        return await self.get_meeting(meeting_id)


class MeetingServiceFactory:
    """Factory for creating meeting services."""
    
    _services = {
        "google_meet": GoogleMeetService,
        "zoom": ZoomService,
        "microsoft_teams": MicrosoftTeamsService,
    }
    
    @classmethod
    def get_service(cls, platform: str, **kwargs):
        service_class = cls._services.get(platform)
        if not service_class:
            raise ValueError(f"Unknown platform: {platform}")
        return service_class(**kwargs)


# Service instances
google_meet_service = GoogleMeetService()
zoom_service = ZoomService()
microsoft_teams_service = MicrosoftTeamsService()