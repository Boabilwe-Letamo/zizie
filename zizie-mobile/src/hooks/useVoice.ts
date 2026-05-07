/**
 * Voice Hook - Core voice processing functionality
 */
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { NativeModules, NativeEventEmitter, Platform, PermissionsAndroid, Alert } from 'react-native';

import { apiService } from '../services/api';


export interface VoiceState {
  isListening: boolean;
  isProcessing: boolean;
  transcript: string;
  response: string;
  error: string | null;
  sessionId: string | null;
  voiceVerified: boolean;
  confidence: number;
  requiresConfirmation: boolean;
}

export interface VoiceContextValue {
  state: VoiceState;
  startListening: () => Promise<void>;
  stopListening: () => void;
  startEnrollment: (profileName: string) => Promise<void>;
  completeEnrollment: () => Promise<void>;
  verifyVoice: (audioData: string) => Promise<boolean>;
  cancelCommand: () => void;
}

const initialState: VoiceState = {
  isListening: false,
  isProcessing: false,
  transcript: '',
  response: '',
  error: null,
  sessionId: null,
  voiceVerified: false,
  confidence: 0,
  requiresConfirmation: false,
};

const VoiceContext = createContext<VoiceContextValue | null>(null);

export const VoiceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<VoiceState>(initialState);
  const [wakeWordModule] = useState<NativeModules | null>(null);
  
  // Initialize wake word detection
  useEffect(() => {
    initializeWakeWord();
    return () => {
      // Cleanup on unmount
      stopListening();
    };
  }, []);
  
  const initializeWakeWord = async () => {
    try {
      if (Platform.OS === 'android') {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          {
            title: 'Microphone Permission',
            message: 'Zizie needs microphone access for voice commands',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          }
        );
        
        if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
          console.warn('Microphone permission not granted');
        }
      }
      
      // Initialize voice processing module
      // Note: In production, integrate with Porcupine for wake word detection
      console.log('Wake word detection initialized');
    } catch (error) {
      console.error('Failed to initialize wake word:', error);
    }
  };
  
  const startListening = useCallback(async () => {
    if (state.isListening || state.isProcessing) {
      return;
    }
    
    setState(prev => ({
      ...prev,
      isListening: true,
      transcript: '',
      response: '',
      error: null,
    }));
    
    try {
      // Start a voice session
      const session = await apiService.startVoiceSession();
      
      setState(prev => ({
        ...prev,
        sessionId: session.session_id,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isListening: false,
        error: 'Failed to start voice session',
      }));
    }
  }, [state.isListening, state.isProcessing]);
  
  const stopListening = useCallback(() => {
    if (!state.isListening) {
      return;
    }
    
    setState(prev => ({
      ...prev,
      isListening: false,
      isProcessing: true,
    }));
  }, [state.isListening]);
  
  const processVoiceCommand = useCallback(async (audioData: string) => {
    try {
      // Send audio to backend for processing
      const result = await apiService.processVoiceAudio(
        audioData,
        state.sessionId || undefined
      );
      
      if (result.needs_confirmation) {
        setState(prev => ({
          ...prev,
          requiresConfirmation: true,
          isProcessing: false,
          response: result.message || result.transcript,
        }));
        
        return;
      }
      
      setState(prev => ({
        ...prev,
        isProcessing: false,
        transcript: result.transcript || '',
        response: result.message || '',
        voiceVerified: result.verified || false,
        confidence: result.confidence || 0,
        requiresConfirmation: false,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isProcessing: false,
        error: 'Failed to process voice command',
      }));
    }
  }, [state.sessionId]);
  
  const startEnrollment = useCallback(async (profileName: string) => {
    try {
      const result = await apiService.startVoiceEnrollment(profileName);
      
      setState(prev => ({
        ...prev,
        transcript: result.challenge_phrase,
      }));
      
      return result;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to start voice enrollment',
      }));
      throw error;
    }
  }, []);
  
  const completeEnrollment = useCallback(async () => {
    try {
      await apiService.completeVoiceEnrollment();
      
      setState(prev => ({
        ...prev,
        transcript: '',
        response: 'Voice enrollment complete',
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to complete enrollment',
      }));
      throw error;
    }
  }, []);
  
  const verifyVoice = useCallback(async (audioData: string): Promise<boolean> => {
    try {
      const result = await apiService.verifyVoice(audioData);
      
      setState(prev => ({
        ...prev,
        voiceVerified: result.verified,
        confidence: result.confidence,
      }));
      
      return result.verified;
    } catch (error) {
      return false;
    }
  }, []);
  
  const cancelCommand = useCallback(() => {
    setState(prev => ({
      ...prev,
      isListening: false,
      isProcessing: false,
      transcript: '',
      response: '',
      requiresConfirmation: false,
    }));
  }, []);
  
  const confirmAction = useCallback(async () => {
    try {
      await apiService.confirmPendingAction();
      
      setState(prev => ({
        ...prev,
        requiresConfirmation: false,
        response: 'Action completed',
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to confirm action',
      }));
    }
  }, []);
  
  const value: VoiceContextValue = {
    state,
    startListening,
    stopListening,
    startEnrollment,
    completeEnrollment,
    verifyVoice,
    cancelCommand,
  };
  
  return (
    <VoiceContext.Provider value={value}>
      {children}
    </VoiceContext.Provider>
  );
};

export const useVoice = (): VoiceContextValue => {
  const context = useContext(VoiceContext);
  
  if (!context) {
    throw new Error('useVoice must be used within a VoiceProvider');
  }
  
  return context;
};

export default useVoice;