# Rule 14B: Mobile Development Standards

<!-- CURSOR: highlight: Cross-platform mobile development with React Native/Flutter, native patterns, performance optimization, and platform-specific considerations -->

## Purpose & Scope

Mobile development standards ensure consistent, performant, and maintainable mobile applications across platforms through standardized architectures, development practices, and optimization techniques. This rule establishes standards for React Native/Flutter development, native iOS/Android patterns, cross-platform architecture, state management, and mobile-specific performance considerations.

<!-- CURSOR: complexity: Intermediate -->

## Core Standards

### React Native Architecture

#### 1. Component Architecture Patterns

**Cross-Platform Component Design:**
```typescript
// components/common/UserCard.tsx
import React, { memo, useMemo } from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  TouchableOpacity,
  Platform,
  Dimensions
} from 'react-native';
import { User } from '@/types/user';
import { useTheme } from '@/hooks/useTheme';
import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { formatDisplayName } from '@/utils/userUtils';

interface UserCardProps {
  user: User;
  onPress?: (user: User) => void;
  showBadge?: boolean;
  variant?: 'compact' | 'expanded';
  testID?: string;
}

/**
 * Cross-platform user card component with responsive design
 * Adapts to platform-specific design patterns and screen sizes
 */
export const UserCard: React.FC<UserCardProps> = memo(({
  user,
  onPress,
  showBadge = true,
  variant = 'compact',
  testID = 'user-card'
}) => {
  const theme = useTheme();
  const { width: screenWidth } = Dimensions.get('window');
  
  // Responsive sizing based on screen width
  const isTablet = screenWidth > 768;
  const cardWidth = isTablet ? screenWidth * 0.4 : screenWidth * 0.9;
  
  const displayName = useMemo(() => 
    formatDisplayName(user), 
    [user]
  );
  
  const styles = useMemo(() => createStyles(theme, variant, cardWidth), [theme, variant, cardWidth]);
  
  const handlePress = () => {
    onPress?.(user);
  };
  
  const CardContent = () => (
    <View style={styles.container}>
      <View style={styles.header}>
        <Avatar
          source={{ uri: user.avatarUrl }}
          size={variant === 'compact' ? 'medium' : 'large'}
          fallbackText={user.firstName.charAt(0) + user.lastName.charAt(0)}
          style={styles.avatar}
        />
        
        <View style={styles.userInfo}>
          <Text style={styles.displayName} numberOfLines={1}>
            {displayName}
          </Text>
          <Text style={styles.email} numberOfLines={1}>
            {user.email}
          </Text>
          
          {variant === 'expanded' && user.bio && (
            <Text style={styles.bio} numberOfLines={2}>
              {user.bio}
            </Text>
          )}
        </View>
        
        {showBadge && user.isOnline && (
          <Badge
            text="Online"
            variant="success"
            size="small"
            style={styles.onlineBadge}
          />
        )}
      </View>
      
      {variant === 'expanded' && (
        <View style={styles.footer}>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{user.postsCount || 0}</Text>
            <Text style={styles.statLabel}>Posts</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{user.followersCount || 0}</Text>
            <Text style={styles.statLabel}>Followers</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{user.followingCount || 0}</Text>
            <Text style={styles.statLabel}>Following</Text>
          </View>
        </View>
      )}
    </View>
  );
  
  if (onPress) {
    return (
      <TouchableOpacity
        onPress={handlePress}
        style={styles.touchable}
        activeOpacity={0.7}
        testID={testID}
        accessibilityRole="button"
        accessibilityLabel={`User card for ${displayName}`}
        accessibilityHint="Tap to view user profile"
      >
        <CardContent />
      </TouchableOpacity>
    );
  }
  
  return (
    <View style={styles.touchable} testID={testID}>
      <CardContent />
    </View>
  );
});

const createStyles = (theme: any, variant: string, cardWidth: number) => StyleSheet.create({
  touchable: {
    width: cardWidth,
    alignSelf: 'center',
    marginVertical: theme.spacing.xs,
  },
  container: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.medium,
    padding: theme.spacing.medium,
    ...Platform.select({
      ios: {
        shadowColor: theme.colors.shadow,
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 3,
      },
    }),
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    marginRight: theme.spacing.medium,
  },
  userInfo: {
    flex: 1,
  },
  displayName: {
    fontSize: variant === 'compact' ? 16 : 18,
    fontWeight: '600',
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.xs,
  },
  email: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    marginBottom: theme.spacing.xs,
  },
  bio: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    lineHeight: 16,
  },
  onlineBadge: {
    marginLeft: theme.spacing.small,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: theme.spacing.medium,
    paddingTop: theme.spacing.medium,
    borderTopWidth: 1,
    borderTopColor: theme.colors.outline,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginTop: theme.spacing.xs,
  },
});

UserCard.displayName = 'UserCard';
```

#### 2. Navigation Patterns

**React Navigation Setup:**
```typescript
// navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { Platform, StatusBar } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { useTheme } from '@/hooks/useTheme';
import { useAuth } from '@/hooks/useAuth';
import { LoadingScreen } from '@/screens/LoadingScreen';
import { AuthStackNavigator } from './AuthStackNavigator';
import { MainTabNavigator } from './MainTabNavigator';
import { ModalStackNavigator } from './ModalStackNavigator';

// Type definitions for navigation
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Modal: {
    screen: string;
    params?: any;
  };
};

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Profile: { userId?: string };
  Settings: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

const RootStack = createNativeStackNavigator<RootStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();
const AuthStack = createNativeStackNavigator<AuthStackParamList>();

// Main Tab Navigator
const MainTabNavigator: React.FC = () => {
  const theme = useTheme();
  
  return (
    <MainTab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;
          
          switch (route.name) {
            case 'Home':
              iconName = focused ? 'home' : 'home';
              break;
            case 'Search':
              iconName = focused ? 'search' : 'search';
              break;
            case 'Profile':
              iconName = focused ? 'person' : 'person-outline';
              break;
            case 'Settings':
              iconName = focused ? 'settings' : 'settings';
              break;
            default:
              iconName = 'circle';
          }
          
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.onSurfaceVariant,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.outline,
          ...Platform.select({
            ios: {
              shadowColor: theme.colors.shadow,
              shadowOffset: { width: 0, height: -2 },
              shadowOpacity: 0.1,
              shadowRadius: 4,
            },
            android: {
              elevation: 8,
            },
          }),
        },
        headerStyle: {
          backgroundColor: theme.colors.surface,
        },
        headerTintColor: theme.colors.onSurface,
        headerTitleStyle: {
          fontWeight: '600',
        },
      })}
    >
      <MainTab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'Home',
          headerShown: false, // Custom header in HomeScreen
        }}
      />
      <MainTab.Screen 
        name="Search" 
        component={SearchScreen}
        options={{
          title: 'Search',
        }}
      />
      <MainTab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profile',
        }}
      />
      <MainTab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          title: 'Settings',
        }}
      />
    </MainTab.Navigator>
  );
};

// Auth Stack Navigator
const AuthStackNavigator: React.FC = () => {
  const theme = useTheme();
  
  return (
    <AuthStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: theme.colors.onPrimary,
        headerTitleStyle: {
          fontWeight: '600',
        },
        presentation: 'card',
        animation: Platform.OS === 'ios' ? 'slide_from_right' : 'slide_from_bottom',
      }}
    >
      <AuthStack.Screen 
        name="Login" 
        component={LoginScreen}
        options={{
          title: 'Sign In',
          headerShown: false, // Custom header in LoginScreen
        }}
      />
      <AuthStack.Screen 
        name="Register" 
        component={RegisterScreen}
        options={{
          title: 'Create Account',
        }}
      />
      <AuthStack.Screen 
        name="ForgotPassword" 
        component={ForgotPasswordScreen}
        options={{
          title: 'Reset Password',
        }}
      />
    </AuthStack.Navigator>
  );
};

// Main App Navigator
export const AppNavigator: React.FC = () => {
  const theme = useTheme();
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <LoadingScreen />;
  }
  
  return (
    <NavigationContainer
      theme={{
        dark: theme.isDark,
        colors: {
          primary: theme.colors.primary,
          background: theme.colors.background,
          card: theme.colors.surface,
          text: theme.colors.onSurface,
          border: theme.colors.outline,
          notification: theme.colors.error,
        },
      }}
    >
      <StatusBar
        barStyle={theme.isDark ? 'light-content' : 'dark-content'}
        backgroundColor={theme.colors.surface}
      />
      <RootStack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        {isAuthenticated ? (
          <>
            <RootStack.Screen 
              name="Main" 
              component={MainTabNavigator}
            />
            <RootStack.Group 
              screenOptions={{ 
                presentation: 'modal',
                animation: 'slide_from_bottom'
              }}
            >
              <RootStack.Screen 
                name="Modal" 
                component={ModalStackNavigator}
              />
            </RootStack.Group>
          </>
        ) : (
          <RootStack.Screen 
            name="Auth" 
            component={AuthStackNavigator}
          />
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
};
```

### State Management for Mobile

#### 1. Redux Toolkit with RTK Query

**Mobile-Optimized State Management:**
```typescript
// store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';

import { apiSlice } from './api/apiSlice';
import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';
import settingsReducer from './slices/settingsSlice';

// Persist configuration
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'settings'], // Only persist these slices
  blacklist: ['api'], // Don't persist API cache
};

const persistedAuthReducer = persistReducer(persistConfig, authReducer);

export const store = configureStore({
  reducer: {
    api: apiSlice.reducer,
    auth: persistedAuthReducer,
    user: userReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }).concat(apiSlice.middleware),
  devTools: __DEV__, // Only enable in development
});

export const persistor = persistStore(store);

// Setup listeners for RTK Query
setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// store/api/apiSlice.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../store';
import Config from 'react-native-config';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: Config.API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('Content-Type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['User', 'Post', 'Comment'],
  endpoints: (builder) => ({
    // User endpoints
    getUser: builder.query<User, string>({
      query: (userId) => `/users/${userId}`,
      providesTags: (result, error, userId) => [{ type: 'User', id: userId }],
    }),
    
    updateUser: builder.mutation<User, { userId: string; updates: Partial<User> }>({
      query: ({ userId, updates }) => ({
        url: `/users/${userId}`,
        method: 'PATCH',
        body: updates,
      }),
      invalidatesTags: (result, error, { userId }) => [{ type: 'User', id: userId }],
    }),
    
    // Posts endpoints
    getPosts: builder.query<Post[], { page?: number; limit?: number }>({
      query: ({ page = 1, limit = 20 }) => `/posts?page=${page}&limit=${limit}`,
      providesTags: ['Post'],
      serializeQueryArgs: ({ endpointName }) => {
        return endpointName;
      },
      merge: (currentCache, newItems, { arg }) => {
        if (arg.page === 1) {
          return newItems;
        }
        return [...currentCache, ...newItems];
      },
      forceRefetch({ currentArg, previousArg }) {
        return currentArg?.page !== previousArg?.page;
      },
    }),
    
    createPost: builder.mutation<Post, Omit<Post, 'id' | 'createdAt'>>({
      query: (post) => ({
        url: '/posts',
        method: 'POST',
        body: post,
      }),
      invalidatesTags: ['Post'],
    }),
    
    // Optimistic updates for likes
    likePost: builder.mutation<{ liked: boolean; likesCount: number }, string>({
      query: (postId) => ({
        url: `/posts/${postId}/like`,
        method: 'POST',
      }),
      onQueryStarted: async (postId, { dispatch, queryFulfilled }) => {
        // Optimistic update
        const patchResult = dispatch(
          apiSlice.util.updateQueryData('getPosts', undefined, (draft) => {
            const post = draft.find((p) => p.id === postId);
            if (post) {
              post.liked = !post.liked;
              post.likesCount += post.liked ? 1 : -1;
            }
          })
        );
        
        try {
          await queryFulfilled;
        } catch {
          // Revert optimistic update on error
          patchResult.undo();
        }
      },
    }),
  }),
});

export const {
  useGetUserQuery,
  useUpdateUserMutation,
  useGetPostsQuery,
  useCreatePostMutation,
  useLikePostMutation,
} = apiSlice;
```

#### 2. Custom Hooks for Mobile

**Mobile-Specific React Hooks:**
```typescript
// hooks/usePlatform.ts
import { Platform, Dimensions, StatusBar } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useState, useEffect } from 'react';

export interface PlatformInfo {
  isIOS: boolean;
  isAndroid: boolean;
  isTablet: boolean;
  screenWidth: number;
  screenHeight: number;
  safeAreaInsets: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  statusBarHeight: number;
}

export const usePlatform = (): PlatformInfo => {
  const insets = useSafeAreaInsets();
  const [dimensions, setDimensions] = useState(Dimensions.get('window'));
  
  useEffect(() => {
    const subscription = Dimensions.addEventListener('change', ({ window }) => {
      setDimensions(window);
    });
    
    return () => subscription?.remove();
  }, []);
  
  return {
    isIOS: Platform.OS === 'ios',
    isAndroid: Platform.OS === 'android',
    isTablet: dimensions.width > 768,
    screenWidth: dimensions.width,
    screenHeight: dimensions.height,
    safeAreaInsets: insets,
    statusBarHeight: Platform.OS === 'android' ? StatusBar.currentHeight || 0 : 0,
  };
};

// hooks/useNetworkStatus.ts
import { useState, useEffect } from 'react';
import NetInfo from '@react-native-netinfo/netinfo';

export interface NetworkStatus {
  isConnected: boolean;
  type: string | null;
  isInternetReachable: boolean | null;
}

export const useNetworkStatus = (): NetworkStatus => {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isConnected: true,
    type: null,
    isInternetReachable: null,
  });
  
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setNetworkStatus({
        isConnected: state.isConnected ?? false,
        type: state.type,
        isInternetReachable: state.isInternetReachable,
      });
    });
    
    return unsubscribe;
  }, []);
  
  return networkStatus;
};

// hooks/useKeyboard.ts
import { useState, useEffect } from 'react';
import { Keyboard, KeyboardEvent } from 'react-native';

export interface KeyboardStatus {
  isVisible: boolean;
  height: number;
}

export const useKeyboard = (): KeyboardStatus => {
  const [keyboardStatus, setKeyboardStatus] = useState<KeyboardStatus>({
    isVisible: false,
    height: 0,
  });
  
  useEffect(() => {
    const showSubscription = Keyboard.addListener('keyboardDidShow', (e: KeyboardEvent) => {
      setKeyboardStatus({
        isVisible: true,
        height: e.endCoordinates.height,
      });
    });
    
    const hideSubscription = Keyboard.addListener('keyboardDidHide', () => {
      setKeyboardStatus({
        isVisible: false,
        height: 0,
      });
    });
    
    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);
  
  return keyboardStatus;
};

// hooks/useAppState.ts
import { useState, useEffect, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';

export const useAppState = (): {
  appState: AppStateStatus;
  isActive: boolean;
  isBackground: boolean;
  isInactive: boolean;
} => {
  const appState = useRef(AppState.currentState);
  const [appStateVisible, setAppStateVisible] = useState(appState.current);
  
  useEffect(() => {
    const subscription = AppState.addEventListener('change', (nextAppState) => {
      appState.current = nextAppState;
      setAppStateVisible(nextAppState);
    });
    
    return () => subscription.remove();
  }, []);
  
  return {
    appState: appStateVisible,
    isActive: appStateVisible === 'active',
    isBackground: appStateVisible === 'background',
    isInactive: appStateVisible === 'inactive',
  };
};
```

### Performance Optimization

#### 1. Image and Asset Optimization

**Optimized Image Component:**
```typescript
// components/ui/OptimizedImage.tsx
import React, { useState, useCallback, memo } from 'react';
import {
  Image,
  ImageStyle,
  View,
  ActivityIndicator,
  Text,
  StyleSheet,
  Platform,
} from 'react-native';
import FastImage, { FastImageProps } from 'react-native-fast-image';

interface OptimizedImageProps {
  source: { uri: string } | number;
  style?: ImageStyle;
  fallbackSource?: { uri: string } | number;
  placeholder?: React.ReactNode;
  errorComponent?: React.ReactNode;
  onLoad?: () => void;
  onError?: (error: any) => void;
  resizeMode?: 'cover' | 'contain' | 'stretch' | 'center';
  priority?: 'low' | 'normal' | 'high';
  cache?: 'immutable' | 'web' | 'cacheOnly';
  testID?: string;
}

/**
 * Optimized image component with caching, lazy loading, and error handling
 * Uses FastImage on Android/iOS for better performance
 */
export const OptimizedImage: React.FC<OptimizedImageProps> = memo(({
  source,
  style,
  fallbackSource,
  placeholder,
  errorComponent,
  onLoad,
  onError,
  resizeMode = 'cover',
  priority = 'normal',
  cache = 'immutable',
  testID = 'optimized-image',
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [imageSource, setImageSource] = useState(source);
  
  const handleLoad = useCallback(() => {
    setLoading(false);
    setError(false);
    onLoad?.();
  }, [onLoad]);
  
  const handleError = useCallback((err: any) => {
    setLoading(false);
    setError(true);
    
    // Try fallback source if available
    if (fallbackSource && imageSource !== fallbackSource) {
      setImageSource(fallbackSource);
      setError(false);
      setLoading(true);
      return;
    }
    
    onError?.(err);
  }, [fallbackSource, imageSource, onError]);
  
  const handleLoadStart = useCallback(() => {
    setLoading(true);
    setError(false);
  }, []);
  
  // Use FastImage for better performance on native platforms
  const ImageComponent = Platform.OS === 'web' ? Image : FastImage;
  
  const imageProps: FastImageProps | any = {
    source: imageSource,
    style: [styles.image, style],
    onLoad: handleLoad,
    onError: handleError,
    onLoadStart: handleLoadStart,
    testID,
    ...(Platform.OS !== 'web' && {
      priority: FastImage.priority[priority],
      cache: FastImage.cacheControl[cache],
      resizeMode: FastImage.resizeMode[resizeMode],
    }),
    ...(Platform.OS === 'web' && {
      resizeMode,
    }),
  };
  
  return (
    <View style={[styles.container, style]}>
      <ImageComponent {...imageProps} />
      
      {loading && (
        <View style={styles.overlay}>
          {placeholder || (
            <ActivityIndicator
              size="small"
              color="#666"
              testID="image-loading-indicator"
            />
          )}
        </View>
      )}
      
      {error && (
        <View style={styles.overlay}>
          {errorComponent || (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>Failed to load image</Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
});

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
  },
  errorContainer: {
    padding: 16,
    alignItems: 'center',
  },
  errorText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
});

OptimizedImage.displayName = 'OptimizedImage';
```

#### 2. List Optimization with FlatList

**Performant List Component:**
```typescript
// components/lists/OptimizedFlatList.tsx
import React, { memo, useCallback, useMemo } from 'react';
import {
  FlatList,
  FlatListProps,
  View,
  Text,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useTheme } from '@/hooks/useTheme';

interface OptimizedFlatListProps<T> extends Omit<FlatListProps<T>, 'renderItem'> {
  data: T[];
  renderItem: ({ item, index }: { item: T; index: number }) => React.ReactElement;
  onRefresh?: () => void;
  refreshing?: boolean;
  onEndReached?: () => void;
  loading?: boolean;
  error?: string | null;
  emptyText?: string;
  itemHeight?: number;
  keyExtractor?: (item: T, index: number) => string;
}

/**
 * Optimized FlatList with performance enhancements and built-in states
 */
export const OptimizedFlatList = <T,>({
  data,
  renderItem,
  onRefresh,
  refreshing = false,
  onEndReached,
  loading = false,
  error = null,
  emptyText = 'No items found',
  itemHeight,
  keyExtractor,
  ...otherProps
}: OptimizedFlatListProps<T>) => {
  const theme = useTheme();
  
  // Memoized render item to prevent unnecessary re-renders
  const memoizedRenderItem = useCallback(
    ({ item, index }: { item: T; index: number }) => {
      return renderItem({ item, index });
    },
    [renderItem]
  );
  
  // Optimized key extractor
  const optimizedKeyExtractor = useCallback(
    (item: T, index: number) => {
      if (keyExtractor) {
        return keyExtractor(item, index);
      }
      // Fallback to index if no key extractor provided
      return index.toString();
    },
    [keyExtractor]
  );
  
  // Get item layout for better performance (if itemHeight provided)
  const getItemLayout = useMemo(() => {
    if (!itemHeight) return undefined;
    
    return (data: any, index: number) => ({
      length: itemHeight,
      offset: itemHeight * index,
      index,
    });
  }, [itemHeight]);
  
  // Handle end reached with debouncing
  const handleEndReached = useCallback(() => {
    if (!loading && onEndReached) {
      onEndReached();
    }
  }, [loading, onEndReached]);
  
  // Render loading footer
  const renderFooter = useCallback(() => {
    if (!loading) return null;
    
    return (
      <View style={styles.footer}>
        <ActivityIndicator size="small" color={theme.colors.primary} />
      </View>
    );
  }, [loading, theme.colors.primary]);
  
  // Render empty state
  const renderEmptyComponent = useCallback(() => {
    if (loading) return null;
    
    return (
      <View style={styles.emptyContainer}>
        <Text style={[styles.emptyText, { color: theme.colors.onSurfaceVariant }]}>
          {error || emptyText}
        </Text>
      </View>
    );
  }, [loading, error, emptyText, theme.colors.onSurfaceVariant]);
  
  // Refresh control
  const refreshControl = useMemo(() => {
    if (!onRefresh) return undefined;
    
    return (
      <RefreshControl
        refreshing={refreshing}
        onRefresh={onRefresh}
        colors={[theme.colors.primary]}
        tintColor={theme.colors.primary}
      />
    );
  }, [onRefresh, refreshing, theme.colors.primary]);
  
  return (
    <FlatList
      data={data}
      renderItem={memoizedRenderItem}
      keyExtractor={optimizedKeyExtractor}
      getItemLayout={getItemLayout}
      refreshControl={refreshControl}
      onEndReached={handleEndReached}
      onEndReachedThreshold={0.1}
      ListFooterComponent={renderFooter}
      ListEmptyComponent={renderEmptyComponent}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={10}
      updateCellsBatchingPeriod={50}
      showsVerticalScrollIndicator={false}
      {...otherProps}
    />
  );
};

const styles = StyleSheet.create({
  footer: {
    padding: 16,
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    textAlign: 'center',
  },
});
```

### Flutter Architecture (Alternative)

#### 1. Flutter Widget Patterns

**Responsive Flutter Widget:**
```dart
// lib/widgets/user_card.dart
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/user.dart';
import '../utils/responsive.dart';

class UserCard extends StatelessWidget {
  final User user;
  final VoidCallback? onTap;
  final bool showBadge;
  final UserCardVariant variant;

  const UserCard({
    Key? key,
    required this.user,
    this.onTap,
    this.showBadge = true,
    this.variant = UserCardVariant.compact,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final responsive = Responsive.of(context);
    final theme = Theme.of(context);
    
    return Card(
      elevation: 2,
      margin: EdgeInsets.symmetric(
        horizontal: responsive.wp(4),
        vertical: responsive.hp(1),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: EdgeInsets.all(responsive.wp(4)),
          child: _buildContent(context, responsive, theme),
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, Responsive responsive, ThemeData theme) {
    return Column(
      children: [
        _buildHeader(responsive, theme),
        if (variant == UserCardVariant.expanded) ...[
          SizedBox(height: responsive.hp(2)),
          _buildStats(responsive, theme),
        ],
      ],
    );
  }

  Widget _buildHeader(Responsive responsive, ThemeData theme) {
    return Row(
      children: [
        _buildAvatar(responsive),
        SizedBox(width: responsive.wp(3)),
        Expanded(child: _buildUserInfo(responsive, theme)),
        if (showBadge && user.isOnline) _buildOnlineBadge(theme),
      ],
    );
  }

  Widget _buildAvatar(Responsive responsive) {
    final size = variant == UserCardVariant.compact 
        ? responsive.wp(12) 
        : responsive.wp(16);
    
    return CircleAvatar(
      radius: size / 2,
      backgroundColor: Colors.grey[300],
      child: ClipOval(
        child: CachedNetworkImage(
          imageUrl: user.avatarUrl ?? '',
          width: size,
          height: size,
          fit: BoxFit.cover,
          placeholder: (context, url) => CircularProgressIndicator(strokeWidth: 2),
          errorWidget: (context, url, error) => Icon(
            Icons.person,
            size: size * 0.6,
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  Widget _buildUserInfo(Responsive responsive, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          user.displayName,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        SizedBox(height: responsive.hp(0.5)),
        Text(
          user.email,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        if (variant == UserCardVariant.expanded && user.bio != null) ...[
          SizedBox(height: responsive.hp(0.5)),
          Text(
            user.bio!,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ],
    );
  }

  Widget _buildOnlineBadge(ThemeData theme) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        'Online',
        style: theme.textTheme.labelSmall?.copyWith(
          color: theme.colorScheme.onPrimary,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildStats(Responsive responsive, ThemeData theme) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildStat('Posts', user.postsCount.toString(), theme),
        _buildStat('Followers', user.followersCount.toString(), theme),
        _buildStat('Following', user.followingCount.toString(), theme),
      ],
    );
  }

  Widget _buildStat(String label, String value, ThemeData theme) {
    return Column(
      children: [
        Text(
          value,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: theme.colorScheme.primary,
          ),
        ),
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

enum UserCardVariant { compact, expanded }

// lib/utils/responsive.dart
import 'package:flutter/material.dart';

class Responsive {
  final BuildContext context;
  late final MediaQueryData _mediaQuery;
  late final double _screenWidth;
  late final double _screenHeight;

  Responsive._(this.context) {
    _mediaQuery = MediaQuery.of(context);
    _screenWidth = _mediaQuery.size.width;
    _screenHeight = _mediaQuery.size.height;
  }

  static Responsive of(BuildContext context) => Responsive._(context);

  // Width percentage
  double wp(double percentage) => _screenWidth * percentage / 100;

  // Height percentage  
  double hp(double percentage) => _screenHeight * percentage / 100;

  // Responsive font size
  double sp(double size) {
    final scaleFactor = _screenWidth / 375; // Base width (iPhone 6/7/8)
    return size * scaleFactor;
  }

  bool get isTablet => _screenWidth > 768;
  bool get isMobile => _screenWidth <= 768;
  bool get isLandscape => _mediaQuery.orientation == Orientation.landscape;
}
```

This rule establishes comprehensive mobile development standards ensuring consistent, performant, and maintainable mobile applications across platforms through standardized architectures, development practices, and optimization techniques. 