/**
 * Settings Screen
 */
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView, ScrollView, Switch } from 'react-native';
import { useAuth } from '../hooks/useAuth';
import { theme } from '../constants/theme';


export const SettingsScreen: React.FC = () => {
  const { logout } = useAuth();
  
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Account</Text>
          <TouchableOpacity style={styles.menuItem}>
            <Text style={styles.menuText}>Profile</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.menuItem}>
            <Text style={styles.menuText}>Voice Settings</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>
          <View style={styles.menuItem}>
            <Text style={styles.menuText}>Language</Text>
            <Text style={styles.menuValue}>English</Text>
          </View>
          <View style={styles.menuItem}>
            <Text style={styles.menuText}>Wake Word</Text>
            <Text style={styles.menuValue}>"Hey Zizie"</Text>
          </View>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notifications</Text>
          <View style={styles.menuItem}>
            <Text style={styles.menuText}>Push Notifications</Text>
            <Switch value={true} />
          </View>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Security</Text>
          <TouchableOpacity style={styles.menuItem}>
            <Text style={styles.menuText}>Manage Voice Profiles</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.menuItem}>
            <Text style={styles.menuText}>Change Password</Text>
          </TouchableOpacity>
        </View>
        
        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  section: { padding: theme.spacing.lg, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  sectionTitle: { fontSize: theme.typography.fontSizes.sm, color: theme.colors.textTertiary, marginBottom: theme.spacing.md },
  menuItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: theme.spacing.md },
  menuText: { fontSize: theme.typography.fontSizes.md, color: theme.colors.text },
  menuValue: { fontSize: theme.typography.fontSizes.md, color: theme.colors.textSecondary },
  logoutButton: { margin: theme.spacing.lg, padding: theme.spacing.md, backgroundColor: theme.colors.error + '20', borderRadius: theme.borderRadius.md, alignItems: 'center' },
  logoutText: { color: theme.colors.error, fontSize: theme.typography.fontSizes.md, fontWeight: theme.typography.fontWeights.semibold },
});

export default SettingsScreen;