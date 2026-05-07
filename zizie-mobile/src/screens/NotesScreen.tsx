/**
 * Notes Screen
 */
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, SafeAreaView, TextInput } from 'react-native';
import { apiService, Note } from '../services/api';
import { theme } from '../constants/theme';

export const NotesScreen: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [search, setSearch] = useState('');
  
  useEffect(() => {
    loadNotes();
  }, []);
  
  const loadNotes = async () => {
    try {
      const data = await apiService.getNotes();
      setNotes(data);
    } catch (error) {
      console.error('Failed to load notes:', error);
    }
  };
  
  const filteredNotes = search ? notes.filter(n => 
    n.content.toLowerCase().includes(search.toLowerCase()) ||
    n.title?.toLowerCase().includes(search.toLowerCase())
  ) : notes;
  
  const renderNote = ({ item }: { item: Note }) => (
    <TouchableOpacity style={styles.noteItem}>
      <Text style={styles.noteTitle}>{item.title || 'Untitled'}</Text>
      <Text style={styles.noteContent} numberOfLines={2}>{item.content}</Text>
      {item.tags?.length > 0 && (
        <View style={styles.tags}>
          {item.tags.map(tag => (
            <Text key={tag} style={styles.tag}>{tag}</Text>
          ))}
        </View>
      )}
    </TouchableOpacity>
  );
  
  return (
    <SafeAreaView style={styles.container}>
      <TextInput
        style={styles.search}
        placeholder="Search notes..."
        value={search}
        onChangeText={setSearch}
      />
      <FlatList
        data={filteredNotes}
        renderItem={renderNote}
        keyExtractor={n => n.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No notes yet</Text>}
      />
      <TouchableOpacity style={styles.fab}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  search: { margin: theme.spacing.md, padding: theme.spacing.md, backgroundColor: theme.colors.backgroundSecondary, borderRadius: theme.borderRadius.md },
  list: { padding: theme.spacing.md },
  noteItem: { padding: theme.spacing.md, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  noteTitle: { fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.semibold },
  noteContent: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textSecondary, marginTop: theme.spacing.xs },
  tags: { flexDirection: 'row', marginTop: theme.spacing.sm, gap: theme.spacing.xs },
  tag: { fontSize: theme.typography.fontSizes.xs, backgroundColor: theme.colors.primary + '20', color: theme.colors.primary, paddingHorizontal: theme.spacing.sm, paddingVertical: 2, borderRadius: theme.borderRadius.sm },
  empty: { textAlign: 'center', color: theme.colors.textTertiary, marginTop: theme.spacing.xl },
  fab: { position: 'absolute', right: theme.spacing.lg, bottom: theme.spacing.lg, width: 56, height: 56, borderRadius: 28, backgroundColor: theme.colors.primary, alignItems: 'center', justifyContent: 'center', ...theme.shadows.lg },
  fabText: { fontSize: 32, color: theme.colors.textInverse },
});

export default NotesScreen;