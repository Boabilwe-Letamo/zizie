"""
Google Calendar and Gmail Service
Provides OAuth flow and API access for Google services
"""
import httpx
from typing import Optional, Dict, Any, List

from app.core.config import settings


class GoogleOAuthService:
    """Google OAuth 2.0 authentication."""
    
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.compose",
        "openid",
        "email",
        "profile"
    ]
    
    @property
    def auth_uri(self) -> str:
        """Generate OAuth authorization URL."""
        import urllib.parse
        
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI
                }
            )
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Token exchange failed: {response.text}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Token refresh failed: {response.text}")


class GoogleCalendarService:
    """Google Calendar API."""
    
    BASE_URL = "https://www.googleapis.com/calendar/v3"
    
    async def get_events(
        self, 
        access_token: str,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get calendar events."""
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "calendarId": "primary",
            "maxResults": max_results,
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/calendars/primary/events",
                headers=headers,
                params=params
            )
        
        if response.status_code == 200:
            return response.json().get("items", [])
        raise Exception(f"Get events failed: {response.text}")
    
    async def create_event(
        self,
        access_token: str,
        title: str,
        start_time: str,
        end_time: str,
        description: str = "",
        attendees: List[str] = None,
        location: str = ""
    ) -> Dict[str, Any]:
        """Create a calendar event."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        event = {
            "summary": title,
            "description": description,
            "location": location,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"}
        }
        
        if attendees:
            event["attendees"] = [{"email": e} for e in attendees]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/calendars/primary/events",
                headers=headers,
                json=event
            )
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Create event failed: {response.text}")


class GoogleGmailService:
    """Gmail API."""
    
    BASE_URL = "https://gmail.googleapis.com/gmail/v1"
    
    async def send_email(
        self,
        access_token: str,
        to: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """Send an email."""
        import base64
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        message = f"To: {to}\nSubject: {subject}\n\n{body}"
        encoded = base64.urlsafe_b64encode(message.encode()).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/users/me/messages/send",
                headers=headers,
                json={"raw": encoded}
            )
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Send failed: {response.text}")


# Instances
google_oauth = GoogleOAuthService()
google_calendar = GoogleCalendarService()
google_gmail = GoogleGmailService()