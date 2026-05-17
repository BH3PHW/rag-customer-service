import { MessageSquare, FileText, Settings, Bot, Users, FileSearch } from 'lucide-react';
import { useAppStore } from './store';
import Chat from './pages/Chat';
import DocumentsPage from './pages/Documents';
import SettingsPage from './pages/Settings';
import UsersPage from './pages/Users';
import CleaningPage from './pages/Cleaning';

export default function App() {
  const { activePage, setActivePage, currentUser, enterpriseId } = useAppStore();

  const navItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare, requireAuth: true },
    { id: 'documents', label: 'Documents', icon: FileText, requireAuth: true },
    { id: 'cleaning', label: 'Cleaning', icon: FileSearch, requireAuth: true },
    { id: 'settings', label: 'Settings', icon: Settings, requireAuth: true },
    { id: 'users', label: 'Profile', icon: Users, requireAuth: false },
  ];

  const renderContent = () => {
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
              <p className="text-xs text-gray-500">Customer Service</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            const isDisabled = item.requireAuth && (!currentUser || !enterpriseId);
            
            return (
              <button
                key={item.id}
                onClick={() => !isDisabled && setActivePage(item.id as any)}
                disabled={isDisabled}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : isDisabled
                    ? 'text-gray-300 cursor-not-allowed'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-400">
            {currentUser ? (
              <div>
                <p className="font-medium text-gray-600">{currentUser.username}</p>
                <p className="text-gray-400">{currentUser.role}</p>
              </div>
            ) : (
              <p className="text-gray-400">Not logged in</p>
            )}
          </div>
        </div>
      </div>
      <div className="flex-1 flex flex-col min-w-0">
        {renderContent()}
      </div>
    </div>
  );
}
