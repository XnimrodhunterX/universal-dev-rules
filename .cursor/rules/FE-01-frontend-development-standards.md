# Rule 14A: Frontend Development Standards

<!-- CURSOR: highlight: Modern frontend development with React/TypeScript, component architecture, performance optimization, and accessibility -->

## Purpose & Scope

Frontend development standards ensure consistent, maintainable, and performant user interfaces through modern frameworks, component architectures, and development practices. This rule establishes standards for React/TypeScript development, component design patterns, state management, performance optimization, and accessibility compliance.

<!-- CURSOR: complexity: Intermediate -->

## Core Standards

### React & TypeScript Architecture

#### 1. Component Design Patterns

**Functional Component Architecture:**
```typescript
// components/user/UserProfile.tsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { User, UserPreferences } from '@/types/user';
import { userService } from '@/services/userService';
import { useAuthContext } from '@/contexts/AuthContext';
import { Button, Card, Avatar, Skeleton } from '@/components/ui';
import { UserPreferencesModal } from './UserPreferencesModal';
import { formatDisplayName } from '@/utils/userUtils';

interface UserProfileProps {
  userId: string;
  isEditable?: boolean;
  onProfileUpdate?: (user: User) => void;
  className?: string;
}

interface UserProfileState {
  user: User | null;
  preferences: UserPreferences | null;
  isLoading: boolean;
  isPreferencesModalOpen: boolean;
  error: string | null;
}

/**
 * UserProfile component displays user information with optional editing capabilities
 * 
 * @example
 * ```tsx
 * <UserProfile 
 *   userId="user123" 
 *   isEditable={true}
 *   onProfileUpdate={handleProfileUpdate}
 * />
 * ```
 */
export const UserProfile: React.FC<UserProfileProps> = ({
  userId,
  isEditable = false,
  onProfileUpdate,
  className = ''
}) => {
  const { currentUser } = useAuthContext();
  const [state, setState] = useState<UserProfileState>({
    user: null,
    preferences: null,
    isLoading: true,
    isPreferencesModalOpen: false,
    error: null
  });

  // Memoized computed values
  const isCurrentUser = useMemo(() => 
    currentUser?.id === userId, 
    [currentUser?.id, userId]
  );

  const displayName = useMemo(() => 
    state.user ? formatDisplayName(state.user) : '',
    [state.user]
  );

  const canEdit = useMemo(() => 
    isEditable && isCurrentUser,
    [isEditable, isCurrentUser]
  );

  // Load user data
  useEffect(() => {
    const loadUserData = async () => {
      try {
        setState(prev => ({ ...prev, isLoading: true, error: null }));
        
        const [user, preferences] = await Promise.all([
          userService.getUser(userId),
          userService.getUserPreferences(userId)
        ]);

        setState(prev => ({
          ...prev,
          user,
          preferences,
          isLoading: false
        }));
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'Failed to load user data',
          isLoading: false
        }));
      }
    };

    if (userId) {
      loadUserData();
    }
  }, [userId]);

  // Event handlers
  const handleEditPreferences = useCallback(() => {
    setState(prev => ({ ...prev, isPreferencesModalOpen: true }));
  }, []);

  const handlePreferencesClose = useCallback(() => {
    setState(prev => ({ ...prev, isPreferencesModalOpen: false }));
  }, []);

  const handlePreferencesUpdate = useCallback(async (newPreferences: UserPreferences) => {
    try {
      await userService.updateUserPreferences(userId, newPreferences);
      setState(prev => ({
        ...prev,
        preferences: newPreferences,
        isPreferencesModalOpen: false
      }));
    } catch (error) {
      console.error('Failed to update preferences:', error);
    }
  }, [userId]);

  const handleProfileEdit = useCallback(async (updatedUser: Partial<User>) => {
    if (!state.user) return;

    try {
      const updated = await userService.updateUser(userId, updatedUser);
      setState(prev => ({ ...prev, user: updated }));
      onProfileUpdate?.(updated);
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  }, [userId, state.user, onProfileUpdate]);

  // Loading state
  if (state.isLoading) {
    return (
      <Card className={`user-profile ${className}`}>
        <div className="user-profile__content">
          <Skeleton className="user-profile__avatar" width={80} height={80} circle />
          <div className="user-profile__details">
            <Skeleton className="user-profile__name" width={200} height={24} />
            <Skeleton className="user-profile__email" width={250} height={16} />
            <Skeleton className="user-profile__bio" width={300} height={48} />
          </div>
        </div>
      </Card>
    );
  }

  // Error state
  if (state.error) {
    return (
      <Card className={`user-profile user-profile--error ${className}`}>
        <div className="user-profile__error">
          <p>Failed to load user profile: {state.error}</p>
          <Button onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  // No user found
  if (!state.user) {
    return (
      <Card className={`user-profile user-profile--not-found ${className}`}>
        <div className="user-profile__not-found">
          <p>User not found</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`user-profile ${className}`} data-testid="user-profile">
      <div className="user-profile__content">
        <div className="user-profile__header">
          <Avatar
            src={state.user.avatarUrl}
            alt={`${displayName} avatar`}
            size="large"
            className="user-profile__avatar"
          />
          <div className="user-profile__details">
            <h2 className="user-profile__name">{displayName}</h2>
            <p className="user-profile__email">{state.user.email}</p>
            {state.user.bio && (
              <p className="user-profile__bio">{state.user.bio}</p>
            )}
          </div>
        </div>

        {canEdit && (
          <div className="user-profile__actions">
            <Button
              variant="secondary"
              onClick={handleEditPreferences}
              data-testid="edit-preferences-button"
            >
              Edit Preferences
            </Button>
          </div>
        )}

        <div className="user-profile__stats">
          <div className="user-profile__stat">
            <span className="user-profile__stat-label">Member since</span>
            <span className="user-profile__stat-value">
              {new Date(state.user.createdAt).toLocaleDateString()}
            </span>
          </div>
          {state.user.lastActiveAt && (
            <div className="user-profile__stat">
              <span className="user-profile__stat-label">Last active</span>
              <span className="user-profile__stat-value">
                {new Date(state.user.lastActiveAt).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>
      </div>

      {state.isPreferencesModalOpen && state.preferences && (
        <UserPreferencesModal
          preferences={state.preferences}
          isOpen={state.isPreferencesModalOpen}
          onClose={handlePreferencesClose}
          onSave={handlePreferencesUpdate}
        />
      )}
    </Card>
  );
};

// Export component with displayName for debugging
UserProfile.displayName = 'UserProfile';

// Default export for lazy loading
export default UserProfile;
```

#### 2. Custom Hooks Pattern

**Reusable State Management Hooks:**
```typescript
// hooks/useAsyncState.ts
import { useState, useCallback, useRef, useEffect } from 'react';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export interface UseAsyncStateReturn<T> {
  state: AsyncState<T>;
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
}

/**
 * Custom hook for managing async operations with loading, error, and success states
 */
export function useAsyncState<T>(
  asyncFunction: (...args: any[]) => Promise<T>,
  immediate = false
): UseAsyncStateReturn<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: immediate,
    error: null
  });

  const mountedRef = useRef(true);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (...args: any[]): Promise<T> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await asyncFunction(...args);
      
      if (mountedRef.current) {
        setState(prev => ({ ...prev, data, loading: false }));
      }
      
      return data;
    } catch (error) {
      if (mountedRef.current) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error : new Error('Unknown error'),
          loading: false
        }));
      }
      throw error;
    }
  }, [asyncFunction]);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null
    });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { state, execute, reset };
}

// hooks/useLocalStorage.ts
import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing localStorage with TypeScript support
 */
export function useLocalStorage<T>(
  key: string,
  defaultValue: T
): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  });

  const setStoredValue = useCallback((newValue: T | ((prev: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, value]);

  const removeStoredValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setValue(defaultValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, defaultValue]);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setValue(JSON.parse(e.newValue));
        } catch (error) {
          console.warn(`Error parsing localStorage change for key "${key}":`, error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  return [value, setStoredValue, removeStoredValue];
}

// hooks/useDebounce.ts
import { useState, useEffect } from 'react';

/**
 * Custom hook for debouncing values
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// hooks/useIntersectionObserver.ts
import { useEffect, useRef, useState } from 'react';

export interface UseIntersectionObserverOptions {
  threshold?: number | number[];
  root?: Element | null;
  rootMargin?: string;
  triggerOnce?: boolean;
}

/**
 * Custom hook for Intersection Observer API
 */
export function useIntersectionObserver(
  options: UseIntersectionObserverOptions = {}
): [React.RefObject<Element>, boolean] {
  const {
    threshold = 0,
    root = null,
    rootMargin = '0%',
    triggerOnce = false
  } = options;

  const elementRef = useRef<Element>(null);
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isElementIntersecting = entry.isIntersecting;
        setIsIntersecting(isElementIntersecting);

        if (isElementIntersecting && triggerOnce) {
          observer.unobserve(element);
        }
      },
      { threshold, root, rootMargin }
    );

    observer.observe(element);

    return () => observer.disconnect();
  }, [threshold, root, rootMargin, triggerOnce]);

  return [elementRef, isIntersecting];
}
```

### State Management Patterns

#### 1. Context API with Reducers

**Global State Management:**
```typescript
// contexts/AppContext.tsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { User } from '@/types/user';
import { Theme } from '@/types/theme';
import { authService } from '@/services/authService';

// State interface
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  theme: Theme;
  notifications: Notification[];
  loading: boolean;
  error: string | null;
}

// Action types
export type AppAction =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }
  | { type: 'SET_THEME'; payload: Theme }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET_STATE' };

// Initial state
const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  theme: 'light',
  notifications: [],
  loading: false,
  error: null
};

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload
      };
    case 'SET_AUTHENTICATED':
      return {
        ...state,
        isAuthenticated: action.payload
      };
    case 'SET_THEME':
      return {
        ...state,
        theme: action.payload
      };
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [...state.notifications, action.payload]
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    case 'RESET_STATE':
      return initialState;
    default:
      return state;
  }
}

// Context
const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

// Provider component
export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Initialize app
  useEffect(() => {
    const initializeApp = async () => {
      dispatch({ type: 'SET_LOADING', payload: true });

      try {
        // Check authentication status
        const isAuthenticated = await authService.checkAuthStatus();
        
        if (isAuthenticated) {
          const user = await authService.getCurrentUser();
          dispatch({ type: 'SET_USER', payload: user });
        }

        // Load theme preference
        const savedTheme = localStorage.getItem('theme') as Theme;
        if (savedTheme) {
          dispatch({ type: 'SET_THEME', payload: savedTheme });
        }
      } catch (error) {
        dispatch({ 
          type: 'SET_ERROR', 
          payload: error instanceof Error ? error.message : 'Initialization failed'
        });
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    initializeApp();
  }, []);

  // Persist theme changes
  useEffect(() => {
    localStorage.setItem('theme', state.theme);
    document.documentElement.setAttribute('data-theme', state.theme);
  }, [state.theme]);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook for using app context
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

// Action creators
export const appActions = {
  setUser: (user: User | null): AppAction => ({
    type: 'SET_USER',
    payload: user
  }),
  
  setTheme: (theme: Theme): AppAction => ({
    type: 'SET_THEME',
    payload: theme
  }),
  
  addNotification: (notification: Omit<Notification, 'id'>): AppAction => ({
    type: 'ADD_NOTIFICATION',
    payload: {
      ...notification,
      id: Date.now().toString()
    }
  }),
  
  removeNotification: (id: string): AppAction => ({
    type: 'REMOVE_NOTIFICATION',
    payload: id
  }),
  
  setError: (error: string | null): AppAction => ({
    type: 'SET_ERROR',
    payload: error
  })
};
```

#### 2. Zustand State Management

**Lightweight State Management:**
```typescript
// stores/userStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { User, UserPreferences } from '@/types/user';
import { userService } from '@/services/userService';

interface UserState {
  // State
  currentUser: User | null;
  preferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setPreferences: (preferences: UserPreferences) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Async actions
  loadUser: (userId: string) => Promise<void>;
  updateUser: (updates: Partial<User>) => Promise<void>;
  updatePreferences: (preferences: UserPreferences) => Promise<void>;
  logout: () => Promise<void>;
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentUser: null,
        preferences: null,
        isLoading: false,
        error: null,

        // Synchronous actions
        setUser: (user) => set({ currentUser: user }, false, 'setUser'),
        setPreferences: (preferences) => set({ preferences }, false, 'setPreferences'),
        setLoading: (isLoading) => set({ isLoading }, false, 'setLoading'),
        setError: (error) => set({ error }, false, 'setError'),

        // Async actions
        loadUser: async (userId: string) => {
          const { setLoading, setError, setUser, setPreferences } = get();
          
          setLoading(true);
          setError(null);

          try {
            const [user, preferences] = await Promise.all([
              userService.getUser(userId),
              userService.getUserPreferences(userId)
            ]);

            setUser(user);
            setPreferences(preferences);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to load user');
          } finally {
            setLoading(false);
          }
        },

        updateUser: async (updates: Partial<User>) => {
          const { currentUser, setUser, setError } = get();
          if (!currentUser) return;

          try {
            const updatedUser = await userService.updateUser(currentUser.id, updates);
            setUser(updatedUser);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to update user');
            throw error;
          }
        },

        updatePreferences: async (preferences: UserPreferences) => {
          const { currentUser, setPreferences, setError } = get();
          if (!currentUser) return;

          try {
            await userService.updateUserPreferences(currentUser.id, preferences);
            setPreferences(preferences);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to update preferences');
            throw error;
          }
        },

        logout: async () => {
          const { setUser, setPreferences, setError } = get();
          
          try {
            await userService.logout();
            setUser(null);
            setPreferences(null);
          } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to logout');
          }
        }
      }),
      {
        name: 'user-store',
        partialize: (state) => ({ 
          currentUser: state.currentUser,
          preferences: state.preferences 
        })
      }
    ),
    { name: 'user-store' }
  )
);

// Selectors for optimized re-renders
export const userSelectors = {
  user: (state: UserState) => state.currentUser,
  preferences: (state: UserState) => state.preferences,
  isLoading: (state: UserState) => state.isLoading,
  error: (state: UserState) => state.error,
  isAuthenticated: (state: UserState) => !!state.currentUser
};
```

### Performance Optimization

#### 1. React Performance Patterns

**Memoization and Optimization:**
```typescript
// components/optimized/ProductList.tsx
import React, { memo, useMemo, useCallback, useState } from 'react';
import { FixedSizeList as List } from 'react-window';
import { Product, ProductFilter } from '@/types/product';
import { useDebounce } from '@/hooks/useDebounce';
import { ProductCard } from './ProductCard';

interface ProductListProps {
  products: Product[];
  onProductSelect: (product: Product) => void;
  filter?: ProductFilter;
  className?: string;
}

// Memoized product card component
const MemoizedProductCard = memo<{
  product: Product;
  onSelect: (product: Product) => void;
  style?: React.CSSProperties;
}>(({ product, onSelect, style }) => {
  const handleSelect = useCallback(() => {
    onSelect(product);
  }, [product, onSelect]);

  return (
    <div style={style}>
      <ProductCard 
        product={product} 
        onSelect={handleSelect}
      />
    </div>
  );
});

MemoizedProductCard.displayName = 'MemoizedProductCard';

// Virtual list item renderer
const ListItem = memo<{
  index: number;
  style: React.CSSProperties;
  data: {
    products: Product[];
    onProductSelect: (product: Product) => void;
  };
}>(({ index, style, data }) => (
  <MemoizedProductCard
    product={data.products[index]}
    onSelect={data.onProductSelect}
    style={style}
  />
));

ListItem.displayName = 'ListItem';

export const ProductList: React.FC<ProductListProps> = memo(({
  products,
  onProductSelect,
  filter,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Memoized filtered products
  const filteredProducts = useMemo(() => {
    let filtered = products;

    // Apply search filter
    if (debouncedSearchTerm) {
      const searchLower = debouncedSearchTerm.toLowerCase();
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchLower) ||
        product.description.toLowerCase().includes(searchLower)
      );
    }

    // Apply additional filters
    if (filter) {
      if (filter.category) {
        filtered = filtered.filter(product => product.category === filter.category);
      }
      if (filter.priceRange) {
        filtered = filtered.filter(product =>
          product.price >= filter.priceRange!.min &&
          product.price <= filter.priceRange!.max
        );
      }
      if (filter.inStock !== undefined) {
        filtered = filtered.filter(product => product.inStock === filter.inStock);
      }
    }

    return filtered;
  }, [products, debouncedSearchTerm, filter]);

  // Memoized list data
  const listData = useMemo(() => ({
    products: filteredProducts,
    onProductSelect
  }), [filteredProducts, onProductSelect]);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  return (
    <div className={`product-list ${className}`}>
      <div className="product-list__header">
        <input
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="product-list__search"
        />
        <div className="product-list__count">
          {filteredProducts.length} products found
        </div>
      </div>

      <div className="product-list__content">
        {filteredProducts.length > 0 ? (
          <List
            height={600}
            itemCount={filteredProducts.length}
            itemSize={120}
            itemData={listData}
            className="product-list__virtual-list"
          >
            {ListItem}
          </List>
        ) : (
          <div className="product-list__empty">
            <p>No products found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
});

ProductList.displayName = 'ProductList';
```

#### 2. Code Splitting and Lazy Loading

**Route-Based Code Splitting:**
```typescript
// App.tsx
import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { AppProvider } from '@/contexts/AppContext';

// Lazy loaded route components
const HomePage = React.lazy(() => import('@/pages/HomePage'));
const ProductsPage = React.lazy(() => import('@/pages/ProductsPage'));
const ProductDetailPage = React.lazy(() => import('@/pages/ProductDetailPage'));
const UserProfilePage = React.lazy(() => import('@/pages/UserProfilePage'));
const SettingsPage = React.lazy(() => import('@/pages/SettingsPage'));
const AdminDashboard = React.lazy(() => import('@/pages/admin/AdminDashboard'));

// Route loading wrapper
const RouteWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ErrorBoundary>
    <Suspense fallback={<LoadingSpinner />}>
      {children}
    </Suspense>
  </ErrorBoundary>
);

export const App: React.FC = () => {
  return (
    <AppProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route 
              path="/" 
              element={
                <RouteWrapper>
                  <HomePage />
                </RouteWrapper>
              } 
            />
            <Route 
              path="/products" 
              element={
                <RouteWrapper>
                  <ProductsPage />
                </RouteWrapper>
              } 
            />
            <Route 
              path="/products/:id" 
              element={
                <RouteWrapper>
                  <ProductDetailPage />
                </RouteWrapper>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <RouteWrapper>
                  <UserProfilePage />
                </RouteWrapper>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <RouteWrapper>
                  <SettingsPage />
                </RouteWrapper>
              } 
            />
            <Route 
              path="/admin/*" 
              element={
                <RouteWrapper>
                  <AdminDashboard />
                </RouteWrapper>
              } 
            />
          </Routes>
        </div>
      </Router>
    </AppProvider>
  );
};
```

### Accessibility Standards

#### 1. ARIA Implementation

**Accessible Component Patterns:**
```typescript
// components/ui/Modal.tsx
import React, { useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useFocusTrap } from '@/hooks/useFocusTrap';
import { useEscapeKey } from '@/hooks/useEscapeKey';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  closeOnBackdropClick?: boolean;
  className?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  closeOnBackdropClick = true,
  className = ''
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Focus trap for accessibility
  useFocusTrap(modalRef, isOpen);

  // Handle escape key
  useEscapeKey(onClose, isOpen);

  // Store and restore focus
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      // Focus the modal after a brief delay to ensure it's rendered
      setTimeout(() => {
        modalRef.current?.focus();
      }, 0);
    } else {
      previousActiveElement.current?.focus();
    }
  }, [isOpen]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = 'unset';
      };
    }
  }, [isOpen]);

  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget && closeOnBackdropClick) {
      onClose();
    }
  }, [onClose, closeOnBackdropClick]);

  if (!isOpen) return null;

  const modalContent = (
    <div 
      className="modal-backdrop"
      onClick={handleBackdropClick}
      data-testid="modal-backdrop"
    >
      <div
        ref={modalRef}
        className={`modal modal--${size} ${className}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby="modal-content"
        tabIndex={-1}
        data-testid="modal"
      >
        <div className="modal__header">
          <h2 id="modal-title" className="modal__title">
            {title}
          </h2>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label="Close modal"
            data-testid="modal-close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        
        <div 
          id="modal-content" 
          className="modal__content"
          data-testid="modal-content"
        >
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

// components/ui/Button.tsx
import React, { forwardRef } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'medium',
  loading = false,
  icon,
  children,
  disabled,
  className = '',
  ...props
}, ref) => {
  const isDisabled = disabled || loading;

  return (
    <button
      ref={ref}
      className={`
        button 
        button--${variant} 
        button--${size} 
        ${loading ? 'button--loading' : ''} 
        ${className}
      `.trim()}
      disabled={isDisabled}
      aria-disabled={isDisabled}
      aria-describedby={loading ? 'loading-indicator' : undefined}
      {...props}
    >
      {loading && (
        <span id="loading-indicator" className="button__spinner" aria-label="Loading">
          <div className="spinner" />
        </span>
      )}
      {icon && <span className="button__icon">{icon}</span>}
      <span className="button__text">{children}</span>
    </button>
  );
});

Button.displayName = 'Button';
```

This rule establishes comprehensive frontend development standards ensuring consistent, maintainable, and performant user interfaces through modern frameworks, component architectures, and development practices.