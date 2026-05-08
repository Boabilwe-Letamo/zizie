/**
 * Home Screen - Clean Voice-First Interface
 * 
 * Focus: Just the microphone and response
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Animated } from 'react-native';
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
        {/* Voice button */}
        <TouchableOpacity
          style={[
            styles.voiceButton,
            state.isListening && styles.voiceButtonActive,
            state.isProcessing && styles.voiceButtonProcessing,
          ]}
          onPress={handleVoicePress}
          disabled={state.isProcessing}
          activeOpacity={0.8}
        >
          <Text style={styles.voiceButtonText}>
            {state.isListening ? '🛑' : state.isProcessing ? '⏳' : '🎤'}
          </Text>
        </TouchableOpacity>
        
        {/* Status */}
        <Text style={styles.statusText}>
          {state.isListening ? 'Listening...' : 
           state.isProcessing ? 'Processing...' : 
           'Tap to speak'}
        </Text>
        
        {/* Response area */}
        {(state.transcript || state.response) && (
          <View style={styles.responseBox}>
            {state.transcript && (
              <View style={styles.textBlock}>
                <Text style={styles.textLabel}>You:</Text>
                <Text style={styles.textValue}>{state.transcript}</Text>
              </View>
            )}
            {state.response && (
              <View style={styles.textBlock}>
                <Text style={[styles.textLabel, { color: theme.colors.primary }]}>Zizie:</Text>
                <Text style={styles.textValue}>{state.response}</Text>
              </View>
            )}
          </View>
        )}
        
        {/* Confirmation */}
        {state.requiresConfirmation && (
          <View style={styles.confirmBox}>
            <Text style={styles.confirmText}>Confirm this action?</Text>
            <View style={styles.confirmButtons}>
              <TouchableOpacity style={styles.confirmBtn}>
                <Text style={styles.confirmBtnText}>✓ Yes</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.confirmBtn, styles.cancelBtn]}
                onPress={cancelCommand}
              >
                <Text style={styles.cancelBtnText}>✗ No</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
        
        {/* Error */}
        {state.error && (
          <Text style={styles.errorText}>{state.error}</Text>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  header: { padding: theme.spacing.lg, alignItems: 'center', paddingTop: theme.spacing.xxl },
  title: { fontSize: 32, fontWeight: 'bold', color: theme.colors.text },
  subtitle: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textSecondary, marginTop: 4 },
  
  content: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: theme.spacing.lg },
  
  voiceButton: {
    width: 140, height: 140, borderRadius: 70,
    backgroundColor: theme.colors.primary,
    alignItems: 'center', justifyContent: 'center',
    ...theme.shadows.lg,
  },
  voiceButtonActive: { backgroundColor: theme.colors.voiceActive },
  voiceButtonProcessing: { backgroundColor: theme.colors.voiceProcessing },
  voiceButtonText: { fontSize: 56 },
  
  statusText: { fontSize: theme.typography.fontSizes.md, color: theme.colors.textSecondary, marginTop: theme.spacing.lg },
  
  responseBox: { marginTop: theme.spacing.xl, width: '100%', gap: theme.spacing.md },
  textBlock: { padding: theme.spacing.md, backgroundColor: theme.colors.backgroundSecondary, borderRadius: theme.borderRadius.md },
  textLabel: { fontSize: theme.typography.fontSizes.xs, color: theme.colors.textTertiary, marginBottom: 4 },
  textValue: { fontSize: theme.typography.fontSizes.md, color: theme.colors.text },
  
  confirmBox: { marginTop: theme.spacing.lg, padding: theme.spacing.md, backgroundColor: theme.colors.warning + '20', borderRadius: theme.borderRadius.md, alignItems: 'center' },
  confirmText: { color: theme.colors.warning, marginBottom: theme.spacing.md },
  confirmButtons: { flexDirection: 'row', gap: theme.spacing.md },
  confirmBtn: { paddingVertical: theme.spacing.sm, paddingHorizontal: theme.spacing.lg, backgroundColor: theme.colors.success, borderRadius: theme.borderRadius.sm },
  confirmBtnText: { color: theme.colors.textInverse, fontWeight: '600' },
  cancelBtn: { backgroundColor: theme.colors.error },
  cancelBtnText: { color: theme.colors.textInverse, fontWeight: '600' },
  
  errorText: { marginTop: theme.spacing.lg, color: theme.colors.error, fontSize: theme.typography.fontSizes.sm },
});

export default HomeScreen;