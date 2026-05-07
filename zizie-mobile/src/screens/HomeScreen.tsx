/**
 * Home Screen - Main voice interaction screen
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { useVoice } from '../hooks/useVoice';
import { theme } from '../constants/theme';


export const HomeScreen: React.FC = () => {
  const { state, startListening, stopListening, cancelCommand } = useVoice();
  
  const handleVoicePress = () => {
    if (state.isListening) {
      stopListening();
    } else {
      startListening();
    }
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Zizie</Text>
        <Text style={styles.subtitle}>Your Voice Assistant</Text>
      </View>
      
      <View style={styles.content}>
        {/* Voice indicator */}
        <TouchableOpacity
          style={[
            styles.voiceButton,
            state.isListening && styles.voiceButtonActive,
            state.isProcessing && styles.voiceButtonProcessing,
          ]}
          onPress={handleVoicePress}
          disabled={state.isProcessing}
        >
          <Text style={styles.voiceButtonText}>
            {state.isListening ? '🛑' : state.isProcessing ? '⏳' : '🎤'}
          </Text>
        </TouchableOpacity>
        
        {/* Status text */}
        <Text style={styles.statusText}>
          {state.isListening && 'Listening...'}
          {state.isProcessing && 'Processing...'}
          {!state.isListening && !state.isProcessing && 'Tap to speak'}
        </Text>
        
        {/* Transcript */}
        {state.transcript && (
          <View style={styles.transcriptContainer}>
            <Text style={styles.transcriptLabel}>You said:</Text>
            <Text style={styles.transcriptText}>{state.transcript}</Text>
          </View>
        )}
        
        {/* Response */}
        {state.response && (
          <View style={styles.responseContainer}>
            <Text style={styles.responseLabel}>Zizie:</Text>
            <Text style={styles.responseText}>{state.response}</Text>
          </View>
        )}
        
        {/* Confirmation */}
        {state.requiresConfirmation && (
          <View style={styles.confirmationContainer}>
            <Text style={styles.confirmationText}>
              This action requires confirmation.
            </Text>
            <View style={styles.confirmationButtons}>
              <TouchableOpacity style={styles.confirmButton}>
                <Text style={styles.confirmButtonText}>Confirm</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={cancelCommand}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        
        {/* Error */}
        {state.error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{state.error}</Text>
          </View>
        )}
      </View>
      
      {/* Quick actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.quickAction}>
          <Text style={styles.quickActionText}>📅 Calendar</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction}>
          <Text style={styles.quickActionText}>✉️ Email</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction}>
          <Text style={styles.quickActionText}>📝 Note</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickAction}>
          <Text style={styles.quickActionText}>⏰ Reminder</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: theme.spacing.lg,
    alignItems: 'center',
  },
  title: {
    fontSize: theme.typography.fontSizes.xxl,
    fontWeight: theme.typography.fontWeights.bold,
    color: theme.colors.text,
  },
  subtitle: {
    fontSize: theme.typography.fontSizes.sm,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing.lg,
  },
  voiceButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: theme.colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    ...theme.shadows.lg,
  },
  voiceButtonActive: {
    backgroundColor: theme.colors.voiceActive,
  },
  voiceButtonProcessing: {
    backgroundColor: theme.colors.voiceProcessing,
  },
  voiceButtonText: {
    fontSize: 48,
  },
  statusText: {
    fontSize: theme.typography.fontSizes.md,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.md,
  },
  transcriptContainer: {
    marginTop: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.md,
    width: '100%',
  },
  transcriptLabel: {
    fontSize: theme.typography.fontSizes.xs,
    color: theme.colors.textTertiary,
  },
  transcriptText: {
    fontSize: theme.typography.fontSizes.md,
    color: theme.colors.text,
    marginTop: theme.spacing.xs,
  },
  responseContainer: {
    marginTop: theme.spacing.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.primaryLight + '20',
    borderRadius: theme.borderRadius.md,
    width: '100%',
  },
  responseLabel: {
    fontSize: theme.typography.fontSizes.xs,
    color: theme.colors.primary,
  },
  responseText: {
    fontSize: theme.typography.fontSizes.md,
    color: theme.colors.text,
    marginTop: theme.spacing.xs,
  },
  confirmationContainer: {
    marginTop: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.warning + '20',
    borderRadius: theme.borderRadius.md,
    width: '100%',
  },
  confirmationText: {
    fontSize: theme.typography.fontSizes.sm,
    color: theme.colors.warning,
    textAlign: 'center',
  },
  confirmationButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: theme.spacing.md,
    gap: theme.spacing.md,
  },
  confirmButton: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.lg,
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.md,
  },
  confirmButtonText: {
    color: theme.colors.textInverse,
    fontWeight: theme.typography.fontWeights.semibold,
  },
  cancelButton: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.lg,
    backgroundColor: theme.colors.error,
    borderRadius: theme.borderRadius.md,
  },
  cancelButtonText: {
    color: theme.colors.textInverse,
    fontWeight: theme.typography.fontWeights.semibold,
  },
  errorContainer: {
    marginTop: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.error + '20',
    borderRadius: theme.borderRadius.md,
    width: '100%',
  },
  errorText: {
    fontSize: theme.typography.fontSizes.sm,
    color: theme.colors.error,
  },
  quickActions: {
    flexDirection: 'row',
    padding: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  quickAction: {
    flex: 1,
    paddingVertical: theme.spacing.sm,
    alignItems: 'center',
  },
  quickActionText: {
    fontSize: theme.typography.fontSizes.xs,
    color: theme.colors.textSecondary,
  },
});

export default HomeScreen;