/**
 * Zizie Mobile - Main App Entry Point
 * Voice-First AI Executive Assistant
 */
import React from 'react';
import { StatusBar, SafeAreaView, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { AppNavigator } from './src/navigation/AppNavigator';
import { VoiceProvider } from './src/hooks/useVoice';
import { AuthProvider } from './src/hooks/useAuth';
import { theme } from './src/constants/theme';


const App: React.FC = () => {
  return (
    <GestureHandlerRootView style={styles.container}>
      <VoiceProvider>
        <AuthProvider>
          <NavigationContainer>
            <SafeAreaView style={styles.container}>
              <StatusBar
                barStyle="dark-content"
                backgroundColor={theme.colors.background}
              />
              <AppNavigator />
            </SafeAreaView>
          </NavigationContainer>
        </AuthProvider>
      </VoiceProvider>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
});

export default App;