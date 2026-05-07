/**
 * Login Screen
 */
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, SafeAreaView, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useAuth } from '../hooks/useAuth';
import { theme } from '../constants/theme';


export const LoginScreen: React.FC = () => {
  const { login, register, isLoading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [fullName, setFullName] = useState('');
  
  const handleSubmit = async () => {
    try {
      if (isRegister) {
        await register(email, password, fullName);
      } else {
        await login(email, password);
      }
    } catch (e) {
      // Error is handled by useAuth
    }
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoid}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <Text style={styles.logo}>🎤</Text>
            <Text style={styles.title}>Zizie</Text>
            <Text style={styles.subtitle}>Your Voice Assistant</Text>
          </View>
          
          <View style={styles.form}>
            {isRegister && (
              <TextInput
                style={styles.input}
                placeholder="Full name"
                value={fullName}
                onChangeText={setFullName}
                autoCapitalize="words"
              />
            )}
            <TextInput
              style={styles.input}
              placeholder="Email"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />
            <TextInput
              style={styles.input}
              placeholder="Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
            
            {error && <Text style={styles.error}>{error}</Text>}
            
            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleSubmit}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>
                {isLoading ? 'Loading...' : isRegister ? 'Create Account' : 'Login'}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.switchButton}
              onPress={() => setIsRegister(!isRegister)}
            >
              <Text style={styles.switchText}>
                {isRegister ? 'Already have an account? Login' : "Don't have an account? Sign up"}
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  keyboardAvoid: { flex: 1 },
  scrollContent: { flexGrow: 1, justifyContent: 'center', padding: theme.spacing.lg },
  header: { alignItems: 'center', marginBottom: theme.spacing.xxl },
  logo: { fontSize: 64 },
  title: { fontSize: theme.typography.fontSizes.xxl, fontWeight: theme.typography.fontWeights.bold, color: theme.colors.text },
  subtitle: { fontSize: theme.typography.fontSizes.md, color: theme.colors.textSecondary, marginTop: theme.spacing.xs },
  form: { padding: theme.spacing.lg },
  input: { backgroundColor: theme.colors.backgroundSecondary, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, marginBottom: theme.spacing.md, fontSize: theme.typography.fontSizes.md },
  error: { color: theme.colors.error, marginBottom: theme.spacing.md, textAlign: 'center' },
  button: { backgroundColor: theme.colors.primary, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, alignItems: 'center' },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: theme.colors.textInverse, fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.semibold },
  switchButton: { marginTop: theme.spacing.md, alignItems: 'center' },
  switchText: { color: theme.colors.primary, fontSize: theme.typography.fontSizes.md },
});

export default LoginScreen;