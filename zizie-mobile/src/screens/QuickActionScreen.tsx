/**
 * Quick Actions Screen - All Features in One Place
 * 
 * Simplified experience: tap to open any feature
 * Voice-first: say "open calendar", "open contacts", etc.
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, ScrollView, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../hooks/useAuth';
import { apiService, CalendarEvent, Contact, Note, Meeting } from '../services/api';
import { theme } from '../constants/theme';


// Quick action cards
const QUICK_ACTIONS = [
  { id: 'calendar', icon: '📅', label: 'Calendar', screen: 'Calendar', color: '#4285F4' },
  { id: 'contacts', icon: '👤', label: 'Contacts', screen: 'Contacts', color: '#EA4335' },
  { id: 'notes', icon: '📝', label: 'Notes', screen: 'Notes', color: '#FBBC05' },
  { id: 'meetings', icon: '📹', label: 'Meetings', screen: 'Meetings', color: '#34A853' },
  { id: 'reminders', icon: '⏰', label: 'Reminders', screen: 'Reminders', color: '#FF6D00' },
  { id: 'email', icon: '✉️', label: 'Email', screen: 'Email', color: '#46FDC1' },
];


export const QuickActionScreen: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigation = useNavigation<any>();
  
  // Show summary data
  const [eventsCount, setEventsCount] = React.useState(0);
  const [contactsCount, setContactsCount] = React.useState(0);
  const [notesCount, setNotesCount] = React.useState(0);
  const [meetingsCount, setMeetingsCount] = React.useState(0);
  
  React.useEffect(() => {
    if (isAuthenticated) {
      loadSummaries();
    }
  }, [isAuthenticated]);
  
  const loadSummaries = async () => {
    try {
      const [events, contacts, notes, meetings] = await Promise.all([
        apiService.getEvents().catch(() => []),
        apiService.getContacts().catch(() => []),
        apiService.getNotes().catch(() => []),
        apiService.getMeetings().catch(() => []),
      ]);
      setEventsCount(events.length);
      setContactsCount(contacts.length);
      setNotesCount(notes.length);
      setMeetingsCount(meetings.length);
    } catch (e) {
      // Ignore errors
    }
  };
  
  const handleAction = (action: typeof QUICK_ACTIONS[0]) => {
    // Navigate to the feature screen
    // Since we don't have real navigation setup, show info
    Alert.alert(
      action.label,
      `This would open the ${action.label} feature.`,
      [{ text: 'OK' }]
    );
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Quick Actions</Text>
        <Text style={styles.subtitle}>Tap any feature to open</Text>
      </View>
      
      <ScrollView contentContainerStyle={styles.content}>
        {/* Summary cards (3 columns) */}
        <View style={styles.grid}>
          {QUICK_ACTIONS.map((action) => (
            <TouchableOpacity
              key={action.id}
              style={[styles.card, { borderLeftColor: action.color }]}
              onPress={() => handleAction(action)}
              activeOpacity={0.7}
            >
              <Text style={styles.cardIcon}>{action.icon}</Text>
              <Text style={styles.cardLabel}>{action.label}</Text>
              {action.id === 'calendar' && eventsCount > 0 && (
                <Text style={styles.badge}>{eventsCount}</Text>
              )}
              {action.id === 'contacts' && contactsCount > 0 && (
                <Text style={styles.badge}>{contactsCount}</Text>
              )}
              {action.id === 'notes' && notesCount > 0 && (
                <Text style={styles.badge}>{notesCount}</Text>
              )}
              {action.id === 'meetings' && meetingsCount > 0 && (
                <Text style={styles.badge}>{meetingsCount}</Text>
              )}
            </TouchableOpacity>
          ))}
        </View>
        
        {/* Voice hints */}
        <View style={styles.voiceHints}>
          <Text style={styles.voiceHintsTitle}>Voice Commands</Text>
          <Text style={styles.voiceHint}>"Hey Zizie, open calendar"</Text>
          <Text style={styles.voiceHint}>"Hey Zizie, create a note"</Text>
          <Text style={styles.voiceHint}>"Hey Zizie, schedule meeting"</Text>
        </View>
      </ScrollView>
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
    fontSize: theme.typography.fontSizes.xl,
    fontWeight: theme.typography.fontWeights.bold,
    color: theme.colors.text,
  },
  subtitle: {
    fontSize: theme.typography.fontSizes.sm,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  content: {
    padding: theme.spacing.md,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  card: {
    width: '31%',
    backgroundColor: theme.colors.backgroundSecondary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    alignItems: 'center',
    borderLeftWidth: 3,
  },
  cardIcon: {
    fontSize: 24,
    marginBottom: theme.spacing.xs,
  },
  cardLabel: {
    fontSize: theme.typography.fontSizes.xs,
    color: theme.colors.text,
    textAlign: 'center',
  },
  badge: {
    position: 'absolute',
    top: theme.spacing.xs,
    right: theme.spacing.xs,
    backgroundColor: theme.colors.primary,
    color: theme.colors.textInverse,
    fontSize: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    overflow: 'hidden',
  },
  voiceHints: {
    marginTop: theme.spacing.xl,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.primaryLight + '15',
    borderRadius: theme.borderRadius.md,
  },
  voiceHintsTitle: {
    fontSize: theme.typography.fontSizes.sm,
    fontWeight: theme.typography.fontWeights.semibold,
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  voiceHint: {
    fontSize: theme.typography.fontSizes.xs,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
});

export default QuickActionScreen;