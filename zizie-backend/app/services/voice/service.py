"""
Voice Service - STT using WhisperX, Speaker Diarization with pyannote
Supports: WhisperX, pyannote, OpenAI Whisper (fallback), Ollama (LLM)
"""
import os
import asyncio
from typing import Optional, List, Dict, Any

import numpy as np

from app.core.config import settings


class TranscriptionResult:
    """Result from speech-to-text."""
    def __init__(self, text: str, segments: List[Dict] = None, language: str = "en"):
        self.text = text
        self.segments = segments or []
        self.language = language


class DiarizationResult:
    """Result from speaker diarization."""
    def __init__(self, segments: List[Dict] = None):
        self.segments = segments or []  # {"start": float, "end": float, "speaker": str, "text": str}


class VoiceService:
    """Unified voice service with WhisperX + pyannote and fallbacks."""
    
    def __init__(self):
        self.whisperx_model = None
        self.diarize_pipeline = None
        self.use_whisperx = settings.USE_WHISPERX
        self.use_pyannote = settings.USE_PYANNOTE
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
    
    # ==================== Speech to Text (WhisperX) ====================
    
    async def speech_to_text(self, audio_data: bytes) -> TranscriptionResult:
        """Convert speech to text with optional timestamps."""
        
        # Try WhisperX first (FREE, local)
        if self.use_whisperx:
            try:
                result = await self._whisperx_stt(audio_data)
                if result.text:
                    return result
            except Exception as e:
                print(f"WhisperX failed: {e}, trying fallback...")
        
        # Fallback to OpenAI Whisper (if API key available)
        if settings.OPENAI_API_KEY:
            try:
                return await self._openai_stt(audio_data)
            except Exception as e:
                print(f"OpenAI Whisper failed: {e}")
        
        # Ultimate fallback
        return TranscriptionResult(text="Voice command received")
    
    async def _whisperx_stt(self, audio_data: bytes) -> TranscriptionResult:
        """Use WhisperX for STT with word-level timestamps."""
        import whisperx
        import io
        import wave
        
        # Load audio
        audio = self._load_audio(audio_data)
        if audio is None:
            return TranscriptionResult("")
        
        # Load model (cache it)
        if self.whisperx_model is None:
            self.whisperx_model = whisperx.load_model(
                settings.WHISPERX_MODEL, 
                device=settings.WHISPERX_DEVICE
            )
        
        # Transcribe
        result = self.whisperx_model.transcribe(audio)
        
        # Merge words into segments
        segments = []
        text_parts = []
        for segment in result.get("segments", []):
            text_parts.append(segment.get("text", ""))
            segments.append({
                "start": segment.get("start", 0),
                "end": segment.get("end", 0),
                "text": segment.get("text", "")
            })
        
        return TranscriptionResult(
            text=" ".join(text_parts),
            segments=segments,
            language=result.get("language", "en")
        )
    
    def _load_audio(self, audio_data: bytes) -> np.ndarray:
        """Load audio data as numpy array."""
        import wave
        import io
        
        try:
            # Try to read as WAV
            with io.BytesIO(audio_data) as f:
                with wave.open(f, 'r') as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    data = wav.readframes(frames)
                    
                    # Convert to float32 numpy array
                    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                    audio = audio / 32768.0  # Normalize
                    
                    return audio
        except Exception as e:
            print(f"Audio load error: {e}")
            return None
    
    async def _openai_stt(self, audio_data: bytes) -> TranscriptionResult:
        """Use OpenAI Whisper API (fallback)."""
        if not settings.OPENAI_API_KEY:
            return TranscriptionResult("")
        
        import base64
        import httpx
        
        audio_b64 = base64.b64encode(audio_data).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                files={"file": ("audio.wav", audio_data, "audio/wav")},
                data={"model": "whisper-1"}
            )
        
        if response.status_code == 200:
            return TranscriptionResult(text=response.json().get("text", ""))
        
        return TranscriptionResult("")
    
    # ==================== Speaker Diarization (pyannote) ====================
    
    async def diarize(self, audio_data: bytes) -> DiarizationResult:
        """Speaker diarization using pyannote."""
        
        if not self.use_pyannote:
            return DiarizationResult()
        
        try:
            return await self._pyannote_diarize(audio_data)
        except Exception as e:
            print(f"pyannote failed: {e}")
            return DiarizationResult()
    
    async def _pyannote_diarize(self, audio_data: bytes) -> DiarizationResult:
        """Use pyannote for speaker diarization."""
        from pyannote.audio import Pipeline
        import torch
        from torch import Tensor
        
        # Load pipeline (cache it)
        if self.diarize_pipeline is None:
            hf_token = settings.HUGGINGFACE_TOKEN
            if hf_token:
                self.diarize_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=hf_token
                )
                if settings.WHISPERX_DEVICE == "cuda":
                    self.diarize_pipeline.to(torch.device("cuda"))
        
        if self.diarize_pipeline is None:
            return DiarizationResult()
        
        # Load audio
        audio = self._load_audio(audio_data)
        if audio is None:
            return DiarizationResult()
        
        # Run diarization
        import torch
        from torch import Tensor
        
        audio_tensor = Tensor(audio).unsqueeze(0)
        diarization = self.diarize_pipeline({"waveform": audio_tensor, "sample_rate": 16000})
        
        # Convert to segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        
        return DiarizationResult(segments=segments)
    
    # ==================== Combined STT + Diarization ====================
    
    async def transcribe_with_diarization(
        self, 
        audio_data: bytes
    ) -> Dict[str, Any]:
        """Get both transcription and speaker segments."""
        # Run in parallel
        transcription, diarization = await asyncio.gather(
            self.speech_to_text(audio_data),
            self.diarize(audio_data)
        )
        
        # Combine results
        combined = {
            "text": transcription.text,
            "language": transcription.language,
            "segments": transcription.segments,
            "speakers": diarization.segments
        }
        
        return combined
    
    # ==================== LLM Processing ====================
    
    async def process_command(self, text: str) -> str:
        """Process voice command with LLM."""
        
        # Try Ollama first (FREE, local)
        if settings.OLLAMA_BASE_URL:
            try:
                return await self._ollama_process(text)
            except Exception as e:
                print(f"Ollama failed: {e}")
        
        # Fallback to OpenAI GPT (if key available)
        if settings.OPENAI_API_KEY:
            try:
                return await self._openai_process(text)
            except Exception as e:
                print(f"OpenAI failed: {e}")
        
        # Ultimate fallback - rule-based
        return self._rule_based_response(text)
    
    async def _ollama_process(self, text: str) -> str:
        """Use Ollama for local LLM."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": f"""You are Zizie, a voice-first AI executive assistant.
                    
User said: {text}

Respond as Zizie would - be brief (under 20 words), helpful, and action-oriented.
Zizie's response:""",
                    "stream": False,
                },
                timeout=60.0
            )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        
        raise Exception("Ollama request failed")
    
    async def _openai_process(self, text: str) -> str:
        """Use OpenAI GPT (fallback)."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Zizie, a voice-first AI executive assistant. Be brief and action-oriented."
                        },
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 100,
                }
            )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        
        raise Exception("OpenAI request failed")
    
    def _rule_based_response(self, text: str) -> str:
        """Simple rule-based responses."""
        text = text.lower()
        
        if "schedule" in text or "meeting" in text:
            return "I'll schedule that for you."
        if "email" in text or "send" in text:
            return "I'll send that email for you."
        if "remind" in text:
            return "I'll set a reminder for you."
        if "note" in text:
            return "I'll create that note for you."
        if "help" in text or "what can" in text:
            return "I can help with calendar, email, notes, and reminders."
        
        return "I understood. Let me help with that."
    
    # ==================== Text to Speech ====================
    
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech (placeholder - use gTTS or Coqui for free)."""
        # Could use gTTS: pip install gTTS
        return b""


# Singleton
voice_service = VoiceService()


# Convenience functions
async def transcribe(audio: bytes) -> TranscriptionResult:
    return await voice_service.speech_to_text(audio)

async def diarize(audio: bytes) -> DiarizationResult:
    return await voice_service.diarize(audio)

async def transcribe_full(audio: bytes) -> Dict[str, Any]:
    return await voice_service.transcribe_with_diarization(audio)

async def process(text: str) -> str:
    return await voice_service.process_command(text)

async def speak(text: str) -> bytes:
    return await voice_service.text_to_speech(text)