/**
 * Calendar Screen
 */
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, SafeAreaView, ScrollView } from 'react-native';
import { apiService, CalendarEvent } from '../services/api';
import { theme } from '../constants/theme';

export const CalendarScreen: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  
  useEffect(() => {
    loadEvents();
  }, []);
  
  const loadEvents = async () => {
    try {
      const data = await apiService.getEvents();
      setEvents(data);
    } catch (error) {
      console.error('Failed to load events:', error);
    }
  };
  
  const renderEvent = ({ item }: { item: CalendarEvent }) => (
    <TouchableOpacity style={styles.eventItem}>
      <Text style={styles.eventTime}>
        {new Date(item.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Text>
      <View style={styles.eventInfo}>
        <Text style={styles.eventTitle}>{item.title}</Text>
        {item.location && <Text style={styles.eventLocation}>{item.location}</Text>}
      </View>
    </TouchableOpacity>
  );
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.dateSelector}>
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <View key={day} style={styles.dayItem}>
            <Text style={styles.dayText}>{day}</Text>
          </View>
        ))}
      </View>
      
      <FlatList
        data={events}
        renderItem={renderEvent}
        keyExtractor={e => e.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No events today</Text>}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  dateSelector: { flexDirection: 'row', padding: theme.spacing.md, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  dayItem: { flex: 1, alignItems: 'center' },
  dayText: { fontSize: theme.typography.fontSizes.xs, color: theme.colors.textSecondary },
  list: { padding: theme.spacing.md },
  eventItem: { flexDirection: 'row', padding: theme.spacing.md, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  eventTime: { width: 60, fontSize: theme.typography.fontSizes.sm, color: theme.colors.primary },
  eventInfo: { flex: 1 },
  eventTitle: { fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.medium },
  eventLocation: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textSecondary },
  empty: { textAlign: 'center', color: theme.colors.textTertiary, marginTop: theme.spacing.xl },
});

export default CalendarScreen;