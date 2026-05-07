/**
 * API Service - REST and WebSocket communication with backend
 */
import { StorageService } from './storage';


// Configure this for your environment
const API_BASE_URL = __DEV__ ? 'http://10.0.2.2:8000' : 'https://api.zizie.app';  // 10.0.2.2 is Android emulator localhost
const WS_URL = __DEV__ ? 'ws://10.0.2.2:8000' : 'wss://api.zizie.app';


export interface VoiceSessionResponse {
  session_id: string;
  commands_count: number;
  status: string;
}

export interface VoiceVerificationResponse {
  verified: boolean;
  profile_id?: string;
  confidence: number;
  permission_level: number;
  requires_confirmation: boolean;
}

export interface VoiceEnrollmentResponse {
  enrollment_id: string;
  challenge_phrase: string;
  challenge_pattern: string;
  message: string;
}

export interface VoiceProcessResponse {
  transcript: string;
  message: string;
  verified: boolean;
  confidence: number;
  needs_confirmation: boolean;
  action_taken?: string;
}

export interface Contact {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  relationships: string[];
}

export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  attendees: string[];
}

export interface Note {
  id: string;
  title?: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface Reminder {
  id: string;
  content: string;
  due_date?: string;
  due_time?: string;
  status: string;
  created_at: string;
}

export interface Meeting {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  platform: 'google_meet' | 'zoom' | 'microsoft_teams';
  meeting_url?: string;
  meeting_id?: string;
  join_info?: string;
  password?: string;
  created_at: string;
}

class APIService {
  private token: string | null = null;
  private websocket: WebSocket | null = null;
  private wsListeners: ((data: any) => void)[] = [];
  
  constructor() {
    this.loadToken();
  }
  
  private async loadToken() {
    this.token = await StorageService.get('auth_token');
  }
  
  private async getHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }
  
  // ==================== Authentication ====================
  
  async register(email: string, password: string, fullName?: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    
    return response.json();
  }
  
  async login(email: string, password: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    this.token = data.access_token;
    await StorageService.set('auth_token', data.access_token);
    
    return data;
  }
  
  async logout() {
    this.token = null;
    await StorageService.remove('auth_token');
  }
  
  // ==================== Voice ====================
  
  async startVoiceSession(): Promise<VoiceSessionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/voice/session/start`, {
      method: 'POST',
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Failed to start voice session');
    }
    
    return response.json();
  }
  
  async endVoiceSession(sessionId: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/voice/session/end`,
      {
        method: 'POST',
        headers: await this.getHeaders(),
        body: JSON.stringify({ session_id: sessionId }),
      }
    );
    
    return response.json();
  }
  
  async startVoiceEnrollment(profileName: string): Promise<VoiceEnrollmentResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/voice/enroll`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify({ profile_name: profileName }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to start enrollment');
    }
    
    return response.json();
  }
  
  async completeVoiceEnrollment() {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/voice/enroll/complete`,
      {
        method: 'POST',
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to complete enrollment');
    }
    
    return response.json();
  }
  
  async addEnrollmentSample(
    audioData: string,
    challengePhrase: string,
    challengePattern: string,
    enrollmentId: string
  ) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/voice/enroll/sample`,
      {
        method: 'POST',
        headers: await this.getHeaders(),
        body: JSON.stringify({
          audio_data: audioData,
          challenge_phrase: challengePhrase,
          expected_pattern: challengePattern,
          enrollment_id: enrollmentId,
        }),
      }
    );
    
    return response.json();
  }
  
  async verifyVoice(audioData: string): Promise<VoiceVerificationResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/voice/verify`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify({ audio_data: audioData }),
    });
    
    if (!response.ok) {
      throw new Error('Voice verification failed');
    }
    
    return response.json();
  }
  
  async processVoiceAudio(
    audioData: string,
    sessionId?: string
  ): Promise<VoiceProcessResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/voice/command`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify({
        audio_data: audioData,
        session_id: sessionId,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to process voice');
    }
    
    return response.json();
  }
  
  async confirmPendingAction() {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/voice/confirm`,
      {
        method: 'POST',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  // ==================== WebSocket ====================
  
  connectWebSocket(sessionId: string) {
    return new Promise<void>((resolve, reject) => {
      try {
        this.websocket = new WebSocket(`${WS_URL}/api/v1/voice/stream/${sessionId}`);
        
        this.websocket.onopen = () => {
          console.log('WebSocket connected');
          resolve();
        };
        
        this.websocket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.wsListeners.forEach(listener => listener(data));
        };
        
        this.websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        this.websocket.onclose = () => {
          console.log('WebSocket disconnected');
          this.websocket = null;
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  disconnectWebSocket() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
  
  sendAudioChunk(audioData: string) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        type: 'audio',
        data: audioData,
      }));
    }
  }
  
  endVoiceCommand() {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        type: 'command',
      }));
    }
  }
  
  addWsListener(listener: (data: any) => void) {
    this.wsListeners.push(listener);
  }
  
  removeWsListener(listener: (data: any) => void) {
    const index = this.wsListeners.indexOf(listener);
    if (index > -1) {
      this.wsListeners.splice(index, 1);
    }
  }
  
  // ==================== Contacts ====================
  
  async getContacts(): Promise<Contact[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/contacts`, {
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get contacts');
    }
    
    return response.json();
  }
  
  async createContact(contact: Omit<Contact, 'id'>): Promise<Contact> {
    const response = await fetch(`${API_BASE_URL}/api/v1/contacts`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(contact),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create contact');
    }
    
    return response.json();
  }
  
  async updateContact(id: string, contact: Partial<Contact>) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/contacts/${id}`,
      {
        method: 'PUT',
        headers: await this.getHeaders(),
        body: JSON.stringify(contact),
      }
    );
    
    return response.json();
  }
  
  async deleteContact(id: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/contacts/${id}`,
      {
        method: 'DELETE',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  async resolveRole(role: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/contacts/resolve/${role}`,
      {
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  // ==================== Calendar ====================
  
  async getEvents(startDate?: string, endDate?: string): Promise<CalendarEvent[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/calendar/events?${params}`,
      {
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to get events');
    }
    
    return response.json();
  }
  
  async createEvent(event: Omit<CalendarEvent, 'id'>): Promise<CalendarEvent> {
    const response = await fetch(`${API_BASE_URL}/api/v1/calendar/events`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(event),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create event');
    }
    
    return response.json();
  }
  
  async updateEvent(id: string, event: Partial<CalendarEvent>) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/calendar/events/${id}`,
      {
        method: 'PUT',
        headers: await this.getHeaders(),
        body: JSON.stringify(event),
      }
    );
    
    return response.json();
  }
  
  async deleteEvent(id: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/calendar/events/${id}`,
      {
        method: 'DELETE',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  // ==================== Notes ====================
  
  async getNotes(tag?: string): Promise<Note[]> {
    const params = tag ? `?tag=${tag}` : '';
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/notes${params}`,
      {
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to get notes');
    }
    
    return response.json();
  }
  
  async createNote(note: { title?: string; content: string; tags?: string[] }): Promise<Note> {
    const response = await fetch(`${API_BASE_URL}/api/v1/notes`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(note),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create note');
    }
    
    return response.json();
  }
  
  async updateNote(id: string, note: Partial<Note>) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/notes/${id}`,
      {
        method: 'PUT',
        headers: await this.getHeaders(),
        body: JSON.stringify(note),
      }
    );
    
    return response.json();
  }
  
  async deleteNote(id: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/notes/${id}`,
      {
        method: 'DELETE',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  async searchNotes(query: string): Promise<Note[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/notes/search?q=${encodeURIComponent(query)}`,
      {
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to search notes');
    }
    
    return response.json();
  }
  
  // ==================== Reminders ====================
  
  async getReminders(status?: string): Promise<Reminder[]> {
    const params = status ? `?status_filter=${status}` : '';
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/reminders${params}`,
      {
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to get reminders');
    }
    
    return response.json();
  }
  
  async createReminder(reminder: {
    content: string;
    due_date?: string;
    due_time?: string;
  }): Promise<Reminder> {
    const response = await fetch(`${API_BASE_URL}/api/v1/reminders`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(reminder),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create reminder');
    }
    
    return response.json();
  }
  
  async completeReminder(id: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/reminders/${id}/complete`,
      {
        method: 'POST',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  async deleteReminder(id: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/reminders/${id}`,
      {
        method: 'DELETE',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
  
  // ==================== Meetings ====================
  
  async getMeetings(platform?: string): Promise<Meeting[]> {
    const params = platform ? `?platform=${platform}` : '';
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1/meetings${params}`,
      {
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to get meetings');
    }
    
    return response.json();
  }
  
  async createMeeting(meeting: {
    title: string;
    description?: string;
    start_time: string;
    end_time: string;
    platform: 'google_meet' | 'zoom' | 'microsoft_teams';
    attendees?: string[];
  }): Promise<Meeting> {
    const response = await fetch(`${API_BASE_URL}/api/v1/meetings`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(meeting),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create meeting');
    }
    
    return response.json();
  }
  
  async quickCreateMeeting(
    title: string,
    platform: 'google_meet' | 'zoom' | 'microsoft_teams' = 'google_meet',
    minutes: number = 60
  ): Promise<Meeting> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/meetings/quick?title=${encodeURIComponent(title)}&platform=${platform}&minutes=${minutes}`,
      {
        method: 'POST',
        headers: await this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to create meeting');
    }
    
    return response.json();
  }
  
  async deleteMeeting(id: string) {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/meetings/${id}`,
      {
        method: 'DELETE',
        headers: await this.getHeaders(),
      }
    );
    
    return response.json();
  }
}

export const apiService = new APIService();