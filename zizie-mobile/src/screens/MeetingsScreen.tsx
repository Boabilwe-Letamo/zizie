/**
 * Meetings Screen - Video meeting management
 */
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, FlatList, Alert, Linking } from 'react-native';
import { useAuth } from '../hooks/useAuth';
import { apiService, Meeting } from '../services/api';
import { theme } from '../constants/theme';


const PLATFORMS = [
  { key: 'google_meet', label: 'Google Meet', icon: '📹' },
  { key: 'zoom', label: 'Zoom', icon: '🎥' },
  { key: 'microsoft_teams', label: 'Teams', icon: '👥' },
];


export const MeetingsScreen: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  
  useEffect(() => {
    if (isAuthenticated) {
      loadMeetings();
    }
  }, [isAuthenticated, selectedPlatform]);
  
  const loadMeetings = async () => {
    try {
      setLoading(true);
      const data = await apiService.getMeetings(selectedPlatform || undefined);
      setMeetings(data);
    } catch (error) {
      console.error('Failed to load meetings:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateMeeting = async (platform: 'google_meet' | 'zoom' | 'microsoft_teams') => {
    try {
      setLoading(true);
      const meeting = await apiService.quickCreateMeeting('Quick Meeting', platform, 60);
      
      Alert.alert(
        'Meeting Created',
        `${platform} meeting ready!`,
        [
          { text: 'Copy Link', onPress: () => {/* Copy to clipboard */} },
          { 
            text: 'Join', 
            onPress: () => {
              if (meeting.meeting_url) {
                Linking.openURL(meeting.meeting_url);
              }
            }
          },
        ]
      );
      
      loadMeetings();
    } catch (error) {
      Alert.alert('Error', 'Failed to create meeting');
    } finally {
      setLoading(false);
    }
  };
  
  const handleJoinMeeting = (url: string) => {
    if (url) {
      Linking.openURL(url);
    }
  };
  
  const handleDeleteMeeting = async (id: string) => {
    Alert.alert('Delete Meeting', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      { 
        text: 'Delete', 
        style: 'destructive',
        onPress: async () => {
          try {
            await apiService.deleteMeeting(id);
            loadMeetings();
          } catch (error) {
            Alert.alert('Error', 'Failed to delete');
          }
        }
      },
    ]);
  };
  
  const renderMeeting = ({ item }: { item: Meeting }) => (
    <TouchableOpacity 
      style={styles.meetingCard}
      onPress={() => item.meeting_url && handleJoinMeeting(item.meeting_url)}
      onLongPress={() => handleDeleteMeeting(item.id)}
    >
      <View style={styles.meetingHeader}>
        <Text style={styles.meetingIcon}>
          {item.platform === 'google_meet' ? '📹' : item.platform === 'zoom' ? '🎥' : '👥'}
        </Text>
        <Text style={styles.meetingTitle}>{item.title}</Text>
      </View>
      
      <Text style={styles.meetingTime}>
        {new Date(item.start_time).toLocaleString()}
      </Text>
      
      {item.meeting_url && (
        <TouchableOpacity 
          style={styles.joinButton}
          onPress={() => handleJoinMeeting(item.meeting_url!)}
        >
          <Text style={styles.joinButtonText}>Join Meeting</Text>
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Meetings</Text>
        <Text style={styles.subtitle}>Video conferences</Text>
      </View>
      
      {/* Quick create buttons */}
      <View style={styles.platformButtons}>
        {PLATFORMS.map((platform) => (
          <TouchableOpacity
            key={platform.key}
            style={styles.platformButton}
            onPress={() => handleCreateMeeting(platform.key as any)}
            disabled={loading}
          >
            <Text style={styles.platformIcon}>{platform.icon}</Text>
            <Text style={styles.platformLabel}>{platform.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
      
      {/* Filter */}
      <View style={styles.filter}>
        <TouchableOpacity
          style={[styles.filterButton, !selectedPlatform && styles.filterActive]}
          onPress={() => setSelectedPlatform(null)}
        >
          <Text style={styles.filterText}>All</Text>
        </TouchableOpacity>
        {PLATFORMS.map((p) => (
          <TouchableOpacity
            key={p.key}
            style={[styles.filterButton, selectedPlatform === p.key && styles.filterActive]}
            onPress={() => setSelectedPlatform(p.key)}
          >
            <Text style={styles.filterText}>{p.label}</Text>
          </TouchableOpacity>
        ))}
      </View>
      
      {/* Meetings list */}
      <FlatList
        data={meetings}
        keyExtractor={(item) => item.id}
        renderItem={renderMeeting}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <Text style={styles.empty}>No meetings yet. Create one above!</Text>
        }
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  header: { padding: theme.spacing.lg, alignItems: 'center' },
  title: { fontSize: theme.typography.fontSizes.xl, fontWeight: theme.typography.fontWeights.bold, color: theme.colors.text },
  subtitle: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textSecondary, marginTop: theme.spacing.xs },
  
  platformButtons: { flexDirection: 'row', padding: theme.spacing.md, gap: theme.spacing.md },
  platformButton: { flex: 1, backgroundColor: theme.colors.primary, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, alignItems: 'center' },
  platformIcon: { fontSize: 24 },
  platformLabel: { fontSize: theme.typography.fontSizes.xs, color: theme.colors.textInverse, marginTop: theme.spacing.xs },
  
  filter: { flexDirection: 'row', paddingHorizontal: theme.spacing.md, gap: theme.spacing.sm },
  filterButton: { paddingVertical: theme.spacing.xs, paddingHorizontal: theme.spacing.md, borderRadius: theme.borderRadius.sm, backgroundColor: theme.colors.backgroundSecondary },
  filterActive: { backgroundColor: theme.colors.primary },
  filterText: { fontSize: theme.typography.fontSizes.xs, color: theme.colors.text },
  
  list: { padding: theme.spacing.md },
  meetingCard: { backgroundColor: theme.colors.backgroundSecondary, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, marginBottom: theme.spacing.md },
  meetingHeader: { flexDirection: 'row', alignItems: 'center', gap: theme.spacing.sm },
  meetingIcon: { fontSize: 20 },
  meetingTitle: { fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.medium, color: theme.colors.text, flex: 1 },
  meetingTime: { fontSize: theme.typography.fontSizes.xs, color: theme.colors.textSecondary, marginTop: theme.spacing.xs },
  
  joinButton: { backgroundColor: theme.colors.success, padding: theme.spacing.sm, borderRadius: theme.borderRadius.sm, alignItems: 'center', marginTop: theme.spacing.md },
  joinButtonText: { color: theme.colors.textInverse, fontSize: theme.typography.fontSizes.sm, fontWeight: theme.typography.fontWeights.medium },
  
  empty: { textAlign: 'center', color: theme.colors.textSecondary, marginTop: theme.spacing.xl },
});

export default MeetingsScreen;