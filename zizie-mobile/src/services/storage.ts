/**
 * Storage Service - Local storage with encryption
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';


const STORAGE_PREFIX = 'zizie_';


class StorageServiceClass {
  private encryptionEnabled: boolean = false;
  
  constructor() {
    this.initializeEncryption();
  }
  
  private async initializeEncryption() {
    try {
      // Try to enable secure storage
      const credentials = await Keychain.getGenericPassword({
        service: 'zizie_keys',
      });
      
      if (credentials) {
        this.encryptionEnabled = true;
      }
    } catch (error) {
      console.warn('Secure storage not available:', error);
    }
  }
  
  private getKey(key: string): string {
    return `${STORAGE_PREFIX}${key}`;
  }
  
  // ==================== Basic Storage ====================
  
  async get(key: string): Promise<string | null> {
    try {
      const value = await AsyncStorage.getItem(this.getKey(key));
      return value;
    } catch (error) {
      console.error('Storage get error:', error);
      return null;
    }
  }
  
  async set(key: string, value: string): Promise<void> {
    try {
      await AsyncStorage.setItem(this.getKey(key), value);
    } catch (error) {
      console.error('Storage set error:', error);
      throw error;
    }
  }
  
  async remove(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(this.getKey(key));
    } catch (error) {
      console.error('Storage remove error:', error);
      throw error;
    }
  }
  
  async has(key: string): Promise<boolean> {
    const value = await this.get(key);
    return value !== null;
  }
  
  // ==================== JSON Storage ====================
  
  async getJSON<T>(key: string): Promise<T | null> {
    try {
      const value = await this.get(key);
      if (value) {
        return JSON.parse(value) as T;
      }
      return null;
    } catch (error) {
      console.error('Storage getJSON error:', error);
      return null;
    }
  }
  
  async setJSON<T>(key: string, value: T): Promise<void> {
    try {
      await this.set(key, JSON.stringify(value));
    } catch (error) {
      console.error('Storage setJSON error:', error);
      throw error;
    }
  }
  
  // ==================== Secure Storage ====================
  
  async setSecure(key: string, value: string): Promise<void> {
    try {
      await Keychain.setGenericPassword(key, value, {
        service: `${STORAGE_PREFIX}${key}`,
        accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY_OR_DEVICE_PASSCODE,
        accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
      });
    } catch (error) {
      console.error('Secure storage set error:', error);
      throw error;
    }
  }
  
  async getSecure(key: string): Promise<string | null> {
    try {
      const credentials = await Keychain.getGenericPassword({
        service: `${STORAGE_PREFIX}${key}`,
      });
      
      if (credentials) {
        return credentials.password;
      }
      return null;
    } catch (error) {
      console.error('Secure storage get error:', error);
      return null;
    }
  }
  
  async removeSecure(key: string): Promise<void> {
    try {
      await Keychain.resetGenericPassword({
        service: `${STORAGE_PREFIX}${key}`,
      });
    } catch (error) {
      console.error('Secure storage remove error:', error);
      throw error;
    }
  }
  
  // ==================== Device ID ====================
  
  async getDeviceId(): Promise<string> {
    let deviceId = await this.get('device_id');
    
    if (!deviceId) {
      deviceId = this.generateUUID();
      await this.set('device_id', deviceId);
    }
    
    return deviceId;
  }
  
  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(
      /[xy]/g,
      (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      }
    );
  }
  
  // ==================== Clear ====================
  
  async clearAll(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const zizieKeys = keys.filter(k => k.startsWith(STORAGE_PREFIX));
      
      await AsyncStorage.multiRemove(zizieKeys);
    } catch (error) {
      console.error('Storage clear error:', error);
      throw error;
    }
  }
}

export const StorageService = new StorageServiceClass();