/**
 * Voice Enrollment Screen
 */
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, SafeAreaView, Alert } from 'react-native';
import { useVoice } from '../hooks/useVoice';
import { theme } from '../constants/theme';

export const VoiceEnrollmentScreen: React.FC = () => {
  const { state, startEnrollment, completeEnrollment, cancelCommand } = useVoice();
  const [profileName, setProfileName] = useState('');
  const [step, setStep] = useState<'name' | 'enroll' | 'complete'>('name');
  const [samples, setSamples] = useState(0);
  
  const handleStart = async () => {
    if (!profileName.trim()) {
      Alert.alert('Error', 'Please enter a profile name');
      return;
    }
    
    try {
      await startEnrollment(profileName.trim());
      setStep('enroll');
    } catch (error) {
      Alert.alert('Error', 'Failed to start enrollment');
    }
  };
  
  const handleRecordSample = async () => {
    // Recording happens automatically
    // This is triggered when user taps record
    setSamples(s => s + 1);
  };
  
  const handleComplete = async () => {
    try {
      await completeEnrollment();
      setStep('complete');
      Alert.alert('Success', 'Voice enrollment complete!', [
        { text: 'OK', onPress: () => cancelCommand() }
      ]);
    } catch (error) {
      Alert.alert('Error', 'Failed to complete enrollment');
    }
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {step === 'name' && (
          <>
            <Text style={styles.title}>Voice Enrollment</Text>
            <Text style={styles.subtitle}>
              Set up your voice ID to use Zizie hands-free
            </Text>
            <TextInput
              style={styles.input}
              placeholder="Enter a name for this profile"
              value={profileName}
              onChangeText={setProfileName}
              autoFocus
            />
            <TouchableOpacity style={styles.button} onPress={handleStart}>
              <Text style={styles.buttonText}>Start</Text>
            </TouchableOpacity>
          </>
        )}
        
        {step === 'enroll' && (
          <>
            <Text style={styles.title}>Speaking...</Text>
            <Text style={styles.subtitle}>
              {state.transcript || 'Speak the phrase shown'}
            </Text>
            
            <View style={styles.recordingIndicator}>
              <Text style={styles.phraseText}>
                {state.transcript || 'Say: "Hey Zizie, schedule my day"'}
              </Text>
            </View>
            
            <Text style={styles.samplesText}>
              Sample {samples + 1} of 5
            </Text>
            
            <TouchableOpacity style={styles.recordButton} onPress={handleRecordSample}>
              <Text style={styles.recordButtonText}>Record</Text>
            </TouchableOpacity>
            
            {samples >= 5 && (
              <TouchableOpacity style={styles.button} onPress={handleComplete}>
                <Text style={styles.buttonText}>Complete</Text>
              </TouchableOpacity>
            )}
          </>
        )}
        
        {step === 'complete' && (
          <>
            <Text style={styles.title}>✓ Complete</Text>
            <Text style={styles.subtitle}>
              Your voice ID is ready to use
            </Text>
            <TouchableOpacity style={styles.button} onPress={cancelCommand}>
              <Text style={styles.buttonText}>Done</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
      
      <TouchableOpacity style={styles.closeButton} onPress={cancelCommand}>
        <Text style={styles.closeText}>Close</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  content: { flex: 1, padding: theme.spacing.lg, justifyContent: 'center' },
  title: { fontSize: theme.typography.fontSizes.xl, fontWeight: theme.typography.fontWeights.bold, textAlign: 'center' },
  subtitle: { fontSize: theme.typography.fontSizes.md, color: theme.colors.textSecondary, textAlign: 'center', marginTop: theme.spacing.sm, marginBottom: theme.spacing.xl },
  input: { backgroundColor: theme.colors.backgroundSecondary, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, fontSize: theme.typography.fontSizes.md, marginBottom: theme.spacing.lg },
  button: { backgroundColor: theme.colors.primary, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, alignItems: 'center' },
  buttonText: { color: theme.colors.textInverse, fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.semibold },
  recordingIndicator: { backgroundColor: theme.colors.primaryLight + '20', padding: theme.spacing.lg, borderRadius: theme.borderRadius.lg, marginBottom: theme.spacing.lg },
  phraseText: { fontSize: theme.typography.fontSizes.lg, textAlign: 'center', color: theme.colors.primary },
  samplesText: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textSecondary, textAlign: 'center', marginBottom: theme.spacing.md },
  recordButton: { width: 80, height: 80, borderRadius: 40, backgroundColor: theme.colors.primary, alignItems: 'center', justifyContent: 'center', alignSelf: 'center', ...theme.shadows.lg },
  recordButtonText: { color: theme.colors.textInverse, fontSize: theme.typography.fontSizes.sm },
  closeButton: { padding: theme.spacing.lg, alignItems: 'center' },
  closeText: { color: theme.colors.textSecondary, fontSize: theme.typography.fontSizes.md },
});

export default VoiceEnrollmentScreen;