import { useState } from 'react';
import { Upload, FileText, Trash2, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useAppStore } from '../store';
import { Document } from '../types';

export default function DocumentsPage() {
  const { documents, addDocument, removeDocument, currentUser } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    if (!currentUser) return;
    
    Array.from(files).forEach((file) => {
      const newDoc: Document = {
        id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
        name: file.name,
        size: file.size,
        uploadDate: new Date(),
        status: 'processing',
        userId: currentUser.id,
      };

      addDocument(newDoc);

      setTimeout(() => {
        removeDocument(newDoc.id);
        addDocument({
          ...newDoc,
          status: 'ready',
        });
      }, 1500);
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'ready':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const userDocuments = currentUser 
    ? documents.filter(d => d.userId === currentUser.id)
    : [];

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">文档</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input')?.click()}
          className={`border-2 border-dashed rounded-lg p-8 mb-6 text-center cursor-pointer transition-all ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <input
            id="file-input"
            type="file"
            multiple
            accept=".txt,.pdf,.md,.docx"
            onChange={handleFileInput}
            className="hidden"
          />
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600 mb-2">拖拽文件到这里或点击上传</p>
          <p className="text-sm text-gray-400">支持 .txt, .pdf, .md, .docx 格式</p>
        </div>
        {userDocuments.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p>暂无文档，请上传文档开始使用</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {userDocuments.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
              >
                <div className="flex-shrink-0">
                  <FileText className="w-10 h-10 text-blue-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 truncate">{doc.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(doc.size)} · {doc.uploadDate.toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(doc.status)}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeDocument(doc.id);
                    }}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
