/**
 * Contacts Screen
 */
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, SafeAreaView, TextInput } from 'react-native';
import { apiService, Contact } from '../services/api';
import { theme } from '../constants/theme';

export const ContactsScreen: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [search, setSearch] = useState('');
  
  useEffect(() => {
    loadContacts();
  }, []);
  
  const loadContacts = async () => {
    try {
      const data = await apiService.getContacts();
      setContacts(data);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    }
  };
  
  const filteredContacts = contacts.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.email?.toLowerCase().includes(search.toLowerCase())
  );
  
  const renderContact = ({ item }: { item: Contact }) => (
    <TouchableOpacity style={styles.contactItem}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{item.name.charAt(0).toUpperCase()}</Text>
      </View>
      <View style={styles.contactInfo}>
        <Text style={styles.contactName}>{item.name}</Text>
        {item.email && <Text style={styles.contactEmail}>{item.email}</Text>}
        {item.relationships?.length > 0 && (
          <Text style={styles.contactRoles}>{item.relationships.join(', ')}</Text>
        )}
      </View>
    </TouchableOpacity>
  );
  
  return (
    <SafeAreaView style={styles.container}>
      <TextInput
        style={styles.search}
        placeholder="Search contacts..."
        value={search}
        onChangeText={setSearch}
      />
      <FlatList
        data={filteredContacts}
        renderItem={renderContact}
        keyExtractor={c => c.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No contacts yet</Text>}
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
  contactItem: { flexDirection: 'row', padding: theme.spacing.md, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  avatar: { width: 40, height: 40, borderRadius: 20, backgroundColor: theme.colors.primary, alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: theme.colors.textInverse, fontWeight: theme.typography.fontWeights.semibold },
  contactInfo: { marginLeft: theme.spacing.md, flex: 1 },
  contactName: { fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.medium },
  contactEmail: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textSecondary },
  contactRoles: { fontSize: theme.typography.fontSizes.xs, color: theme.colors.primary },
  empty: { textAlign: 'center', color: theme.colors.textTertiary, marginTop: theme.spacing.xl },
  fab: { position: 'absolute', right: theme.spacing.lg, bottom: theme.spacing.lg, width: 56, height: 56, borderRadius: 28, backgroundColor: theme.colors.primary, alignItems: 'center', justifyContent: 'center', ...theme.shadows.lg },
  fabText: { fontSize: 32, color: theme.colors.textInverse },
});

export default ContactsScreen;