import React from "react";
import {
  MessageSquare,
  FileText,
  Lightbulb,
  HelpCircle,
  GitBranch,
  Brain,
  Layers,
  Scale,
  BookOpen,
  Code2,
  AlertTriangle,
  Route,
} from "lucide-react";

export const NAV_ITEMS = [
  { key: "chat", label: "Chat", icon: MessageSquare },
  { key: "summary", label: "Summary", icon: FileText },
  { key: "concepts", label: "Concepts", icon: Lightbulb },
  { key: "questions", label: "Questions", icon: HelpCircle },
  { key: "mindmap", label: "Mind Map", icon: GitBranch },
  { key: "quiz", label: "Quiz", icon: Brain },
  { key: "flashcards", label: "Flashcards", icon: Layers },
  { key: "counterargs", label: "Counter Arguments", icon: Scale },
  { key: "explain_simple", label: "Explain Simply", icon: BookOpen },
  { key: "explain_technical", label: "Technical Explanation", icon: Code2 },
  { key: "missing_knowledge", label: "Knowledge Gaps", icon: AlertTriangle },
  { key: "roadmap", label: "Roadmap", icon: Route },
];

const Sidebar = ({ mode, setMode, docId }) => {
  return (
    <aside className="w-64 h-screen border-r border-line bg-white flex flex-col overflow-y-auto">
      <div className="px-6 py-6 border-b border-line">
        <h1 className="text-lg font-semibold text-ink tracking-tight">
          AI Knowledge Studio
        </h1>
        <p className="text-xs text-muted mt-1">Document intelligence</p>
      </div>

      <nav className="flex-1 px-3 py-5 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = mode === item.key;

          return (
            <button
              key={item.key}
              onClick={() => setMode(item.key)}
              className={`group relative w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-black text-white"
                  : "text-muted hover:bg-gray-50 hover:text-ink"
              }`}
            >
              <Icon
                size={17}
                strokeWidth={2}
                className={
                  isActive
                    ? "text-white"
                    : "text-muted group-hover:text-ink"
                }
              />
              <span className="text-xs">{item.label}</span>
            </button>
          );
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
              {docId ? docId : "No document loaded"}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;