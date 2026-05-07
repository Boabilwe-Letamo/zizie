/**
 * Theme Constants
 * Zizie Design System
 */

export const theme = {
  colors: {
    // Primary colors
    primary: '#2563EB',        // Blue - main brand color
    primaryLight: '#3B82F6',
    primaryDark: '#1D4ED8',
    
    // Secondary colors
    secondary: '#10B981',       // Green - success/action
    secondaryLight: '#34D399',
    secondaryDark: '#059669',
    
    // Background colors
    background: '#FFFFFF',
    backgroundSecondary: '#F3F4F6',
    backgroundTertiary: '#E5E7EB',
    
    // Text colors
    text: '#111827',
    textSecondary: '#6B7280',
    textTertiary: '#9CA3AF',
    textInverse: '#FFFFFF',
    
    // Status colors
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    
    // UI colors
    border: '#E5E7EB',
    divider: '#F3F4F6',
    overlay: 'rgba(0, 0, 0, 0.5)',
    
    // Voice indicator colors
    voiceActive: '#10B981',
    voiceProcessing: '#F59E0B',
    voiceInactive: '#9CA3AF',
    voiceError: '#EF4444',
  },
  
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16,
    xl: 24,
    round: 999,
  },
  
  typography: {
    fontSizes: {
      xs: 12,
      sm: 14,
      md: 16,
      lg: 18,
      xl: 24,
      xxl: 32,
      xxxl: 48,
    },
    
    fontWeights: {
      regular: '400' as const,
      medium: '500' as const,
      semibold: '600' as const,
      bold: '700' as const,
    },
    
    lineHeights: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  
  shadows: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 2,
      elevation: 1,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 5,
    },
  },
  
  animation: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
};

export type Theme = typeof theme;