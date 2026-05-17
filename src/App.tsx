import { MessageSquare, FileText, Settings, Bot, Users, FileSearch } from 'lucide-react';
import { useAppStore } from './store';
import Chat from './pages/Chat';
import DocumentsPage from './pages/Documents';
import SettingsPage from './pages/Settings';
import UsersPage from './pages/Users';
import CleaningPage from './pages/Cleaning';

export default function App() {
  const { activePage, setActivePage, currentUser } = useAppStore();

  const navItems = [
    { id: 'chat', label: '聊天', icon: MessageSquare },
    { id: 'documents', label: '文档', icon: FileText },
    { id: 'cleaning', label: '清洗', icon: FileSearch },
    { id: 'settings', label: '设置', icon: Settings },
    { id: 'users', label: '用户', icon: Users },
  ];

  const renderContent = () => {
    if (!currentUser && activePage !== 'users') {
      return <UsersPage />;
    }
    
    switch (activePage) {
      case 'chat':
        return <Chat />;
      case 'documents':
        return <DocumentsPage />;
      case 'cleaning':
        return <CleaningPage />;
      case 'settings':
        return <SettingsPage />;
      case 'users':
        return <UsersPage />;
      default:
        return <Chat />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-800">RAG Agent</h1>
              <p className="text-xs text-gray-500">知识助手</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id as any)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                  activePage === item.id
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
      <div className="flex-1 flex flex-col min-w-0">
        {renderContent()}
      </div>
    </div>
  );
}
