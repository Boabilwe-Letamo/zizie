/**
 * Navigation Configuration
 */
import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../hooks/useAuth';

import { theme } from '../constants/theme';

// Screens
import { HomeScreen } from '../screens/HomeScreen';
import { SettingsScreen } from '../screens/SettingsScreen';
import { ContactsScreen } from '../screens/ContactsScreen';
import { CalendarScreen } from '../screens/CalendarScreen';
import { NotesScreen } from '../screens/NotesScreen';
import { VoiceEnrollmentScreen } from '../screens/VoiceEnrollmentScreen';
import { LoginScreen } from '../screens/LoginScreen';

// Icons (placeholder)
const TabIcon = ({ name, color }: { name: string; color: string }) => (
  <React.Fragment>{name}</React.Fragment>
);

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();


const MainTabs: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textTertiary,
        tabBarStyle: {
          backgroundColor: theme.colors.background,
          borderTopColor: theme.colors.border,
          paddingTop: theme.spacing.xs,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: theme.typography.fontSizes.xs,
          fontWeight: theme.typography.fontWeights.medium,
        },
        headerShown: false,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarLabel: 'Home',
          tabBarIcon: ({ color }) => (
            <TabIcon name="🏠" color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Calendar"
        component={CalendarScreen}
        options={{
          tabBarLabel: 'Calendar',
          tabBarIcon: ({ color }) => (
            <TabIcon name="📅" color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Contacts"
        component={ContactsScreen}
        options={{
          tabBarLabel: 'Contacts',
          tabBarIcon: ({ color }) => (
            <TabIcon name="👤" color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Notes"
        component={NotesScreen}
        options={{
          tabBarLabel: 'Notes',
          tabBarIcon: ({ color }) => (
            <TabIcon name="📝" color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarLabel: 'Settings',
          tabBarIcon: ({ color }) => (
            <TabIcon name="⚙️" color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};


export const AppNavigator: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    // Show loading screen while checking auth
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Loading" component={HomeScreen} />
      </Stack.Navigator>
    );
  }
  
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.background,
        },
        headerTintColor: theme.colors.text,
        headerTitleStyle: {
          fontWeight: theme.typography.fontWeights.semibold,
        },
        headerShadowVisible: false,
      }}
    >
      {!isAuthenticated ? (
        // Auth screens
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
      ) : (
        // Main screens
        <Stack.Screen
          name="MainTabs"
          component={MainTabs}
          options={{ headerShown: false }}
        />
      )}
      
      {/* Overlay screens */}
      <Stack.Screen
        name="VoiceEnrollment"
        component={VoiceEnrollmentScreen}
        options={{
          presentation: 'modal',
          headerShown: false,
        }}
      />
    </Stack.Navigator>
  );
};

export default AppNavigator;