import React from 'react'
import { MessageSquare, BarChart3, HelpCircle, FileText } from 'lucide-react'

const NAV_ITEMS = [
  { key: 'chat', label: 'Chat', icon: MessageSquare },
  { key: 'analysis', label: 'Analysis', icon: BarChart3 },
  { key: 'quiz', label: 'Quiz', icon: HelpCircle },
]

const Sidebar = ({ activeView, onChangeView, docId }) => {
  return (
    <aside className="w-64 h-screen border-r border-line bg-white flex flex-col">
      <div className="px-6 py-6 border-b border-line">
        <h1 className="text-lg font-semibold text-ink tracking-tight">
          AI Knowledge Studio
        </h1>
        <p className="text-xs text-muted mt-1">Document intelligence</p>
      </div>

      <nav className="flex-1 px-3 py-5 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = activeView === item.key
          const Icon = item.icon
          return (
            <button
              key={item.key}
              onClick={() => onChangeView(item.key)}
              className={`group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-accentSoft text-accent'
                  : 'text-muted hover:bg-gray-50 hover:text-ink'
              }`}
            >
              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-0.5 rounded-full bg-accent" />
              )}
              <Icon
                size={17}
                strokeWidth={2}
                className={isActive ? 'text-accent' : 'text-muted group-hover:text-ink'}
              />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div className="px-4 py-4 border-t border-line">
        <div className="flex items-center gap-3 rounded-xl bg-gray-50 px-3 py-3">
          <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-white border border-line shrink-0">
            <FileText size={15} className="text-muted" />
          </div>
          <div className="min-w-0">
            <p className="text-xs text-muted">Active document</p>
            <p className="text-sm text-ink truncate">
              {docId ? docId : 'No document loaded'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar