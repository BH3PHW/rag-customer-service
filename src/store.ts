import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Message, Document, AppSettings, User, CleaningRule, CleaningJob } from './types';

interface AppState {
  activePage: 'chat' | 'documents' | 'settings' | 'users' | 'cleaning';
  currentUser: User | null;
  users: User[];
  messages: Message[];
  documents: Document[];
  cleaningRules: CleaningRule[];
  cleaningJobs: CleaningJob[];
  settings: AppSettings;
  isLoading: boolean;
  
  // 用户管理
  setCurrentUser: (user: User | null) => void;
  login: (username: string, password: string) => boolean;
  register: (username: string, email: string, password: string) => boolean;
  logout: () => void;
  addUser: (user: User) => void;
  removeUser: (id: string) => void;
  
  // 数据清洗
  setCleaningRules: (rules: CleaningRule[]) => void;
  addCleaningRule: (rule: CleaningRule) => void;
  removeCleaningRule: (id: string) => void;
  updateCleaningRule: (id: string, updates: Partial<CleaningRule>) => void;
  addCleaningJob: (job: CleaningJob) => void;
  updateCleaningJob: (id: string, updates: Partial<CleaningJob>) => void;
  removeCleaningJob: (id: string) => void;
  
  // 现有功能
  setActivePage: (page: 'chat' | 'documents' | 'settings' | 'users' | 'cleaning') => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
  updateSettings: (settings: Partial<AppSettings>) => void;
  setIsLoading: (loading: boolean) => void;
}

const defaultSettings: AppSettings = {
  apiKey: '',
  apiEndpoint: 'https://api.openai.com/v1',
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
  topP: 0.9,
  topK: 5,
  chunkSize: 1000,
  chunkOverlap: 200,
};

const defaultCleaningRules: CleaningRule[] = [
  { id: '1', name: '移除多余空白', type: 'remove_whitespace', enabled: true },
  { id: '2', name: '移除多余换行', type: 'remove_newlines', enabled: true },
  { id: '3', name: '移除特殊字符', type: 'remove_special_chars', enabled: false },
];

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      activePage: 'chat',
      currentUser: null,
      users: [
        { id: '1', username: 'admin', email: 'admin@example.com', role: 'admin', createdAt: new Date() },
      ],
      messages: [],
      documents: [],
      cleaningRules: defaultCleaningRules,
      cleaningJobs: [],
      settings: defaultSettings,
      isLoading: false,
      
      // 用户管理方法
      setCurrentUser: (user) => set({ currentUser: user }),
      login: (username, password) => {
        // 简单的模拟登录
        const { users } = get();
        const user = users.find(u => u.username === username);
        if (user) {
          set({ currentUser: user });
          return true;
        }
        return false;
      },
      register: (username, email, password) => {
        const { users } = get();
        const exists = users.some(u => u.username === username || u.email === email);
        if (exists) return false;
        
        const newUser: User = {
          id: Date.now().toString(),
          username,
          email,
          role: 'user',
          createdAt: new Date(),
        };
        set({ users: [...users, newUser], currentUser: newUser });
        return true;
      },
      logout: () => set({ currentUser: null }),
      addUser: (user) => set((state) => ({ users: [...state.users, user] })),
      removeUser: (id) => set((state) => ({ 
        users: state.users.filter(u => u.id !== id) 
      })),
      
      // 数据清洗方法
      setCleaningRules: (rules) => set({ cleaningRules: rules }),
      addCleaningRule: (rule) => set((state) => ({ 
        cleaningRules: [...state.cleaningRules, rule] 
      })),
      removeCleaningRule: (id) => set((state) => ({ 
        cleaningRules: state.cleaningRules.filter(r => r.id !== id) 
      })),
      updateCleaningRule: (id, updates) => set((state) => ({
        cleaningRules: state.cleaningRules.map(r => 
          r.id === id ? { ...r, ...updates } : r
        )
      })),
      addCleaningJob: (job) => set((state) => ({ 
        cleaningJobs: [...state.cleaningJobs, job] 
      })),
      updateCleaningJob: (id, updates) => set((state) => ({
        cleaningJobs: state.cleaningJobs.map(j => 
          j.id === id ? { ...j, ...updates } : j
        )
      })),
      removeCleaningJob: (id) => set((state) => ({ 
        cleaningJobs: state.cleaningJobs.filter(j => j.id !== id) 
      })),
      
      // 现有方法
      setActivePage: (page) => set({ activePage: page }),
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
      })),
      clearMessages: () => set({ messages: [] }),
      addDocument: (document) => set((state) => ({
        documents: [...state.documents, document]
      })),
      removeDocument: (id) => set((state) => ({
        documents: state.documents.filter((d) => d.id !== id)
      })),
      updateSettings: (newSettings) => set((state) => ({
        settings: { ...state.settings, ...newSettings }
      })),
      setIsLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'rag-app-storage',
    }
  )
);
