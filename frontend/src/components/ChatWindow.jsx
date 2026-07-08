import React, { useRef, useEffect, useReducer } from "react";
import { Send, Bot, User, ArrowRight } from "lucide-react";
import UploadPanel from "./UploadPanel.jsx";
import ResponseRenderer from "./ResponseRenderer.jsx";
import axios from "axios";

const backendUrl = import.meta.env.VITE_BACKEND_URL;

const initialState = {
  mode: "chat",
  query: "",
  documentId: null,
  sessionId: null,
  response: null,
  loading: false,
  error: null,
};

function reducer(state, action) {
  switch (action.type) {
    case "SET_MODE":
      return { ...state, mode: action.payload };
    case "SET_QUERY":
      return { ...state, query: action.payload };
    case "SET_DOCUMENT_ID":
      return { ...state, documentId: action.payload };
    case "SET_SESSION_ID":
      return { ...state, sessionId: action.payload };
    case "SET_RESPONSE":
      return { ...state, response: action.payload };
    case "SET_LOADING":
      return { ...state, loading: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload };
    case "RESET":
      return {
        ...initialState,
        sessionId: crypto.randomUUID(),
      };
    default:
      return state;
  }
}

const formatChatText = (text) => {
  if (!text) return "";
  return String(text)
    .replace(/\r\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/\t/g, "  ")
    .trim();
};

const ChatWindow = ({ mode }) => {
  const [messages, setMessages] = React.useState([]);
  const [showUpload, setShowUpload] = React.useState(false);

  const [state, dispatch] = useReducer(reducer, {
    ...initialState,
    sessionId: crypto.randomUUID(),
  });

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, state.loading]);

  const sendMessage = async () => {
    const text = state.query.trim();
    if (!text || state.loading) return;

    const userMessage = { role: "user", text };
    setMessages((prev) => [...prev, userMessage]);

    dispatch({ type: "SET_QUERY", payload: "" });
    dispatch({ type: "SET_LOADING", payload: true });
    dispatch({ type: "SET_ERROR", payload: null });

    const payload = {
      query: text,
      session_id: state.sessionId,
      document_id: state.documentId,
      chain_type: mode,
    };

    try {
      const { data } = await axios.post(`${backendUrl}/chat/model`, payload);
      dispatch({ type: "SET_RESPONSE", payload: data });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          mode,
          data: data?.response ?? data,
        },
      ]);
    } catch (err) {
      dispatch({
        type: "SET_ERROR",
        payload: err?.response?.data?.detail || err?.message || "Something went wrong",
      });
    } finally {
      dispatch({ type: "SET_LOADING", payload: false });
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="relative flex flex-col h-screen bg-white w-full p-3">
      <div className="relative z-50 flex flex-row items-center justify-end mr-10">
        {!showUpload && (
          <button
            onClick={() => setShowUpload(true)}
            className="bg-black text-white px-4 py-2 rounded-md"
          >
            UploadDocument
          </button>
        )}
      </div>

      {showUpload && (
        <div className="absolute inset-0 bg-white z-50 h-screen px-10 py-6">
          <div className="flex flex-row items-center justify-end">
            <button
              onClick={() => setShowUpload(false)}
              className="cursor-pointer"
            >
              <ArrowRight />
            </button>
          </div>

          <div>
            <UploadPanel />
          </div>
        </div>
      )}

      <div className="relative flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-5">
          {messages.map((msg, i) => {
            const isUser = msg.role === "user";
            const isChatAssistant = msg.role === "assistant" && msg.mode === "chat";

            const content =
              typeof msg.data === "string"
                ? formatChatText(msg.data)
                : formatChatText(msg.data?.response || msg.data?.answer || "No response received.");

            return (
              <div
                key={i}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="h-8 w-8 rounded-full flex items-center justify-center bg-gray-200 shrink-0 mt-1">
                    <Bot size={16} />
                  </div>
                )}

                {isUser ? (
                  <div className="max-w-[80%] rounded-2xl bg-black text-white px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-sm">
                    {msg.text}
                  </div>
                ) : isChatAssistant ? (
                  <div className="max-w-[85%] rounded-2xl bg-slate-50 border border-slate-200 px-4 py-3 text-sm leading-7 text-slate-800 shadow-sm whitespace-pre-wrap">
                    {content.split("\n").map((line, idx) => {
                      const trimmed = line.trim();

                      if (!trimmed) {
                        return <div key={idx} className="h-2" />;
                      }

                      if (/^#{1,3}\s/.test(trimmed)) {
                        const level = trimmed.match(/^#{1,3}/)[0].length;
                        const text = trimmed.replace(/^#{1,3}\s/, "");
                        const Tag = level === 1 ? "h1" : level === 2 ? "h2" : "h3";

                        return (
                          <Tag
                            key={idx}
                            className={`font-semibold text-slate-900 ${
                              level === 1
                                ? "text-lg"
                                : level === 2
                                ? "text-base"
                                : "text-sm"
                            }`}
                          >
                            {text}
                          </Tag>
                        );
                      }

                      if (/^[-*]\s/.test(trimmed)) {
                        return (
                          <div key={idx} className="flex gap-2">
                            <span className="mt-2 h-1.5 w-1.5 rounded-full bg-slate-500 shrink-0" />
                            <span>{trimmed.replace(/^[-*]\s/, "")}</span>
                          </div>
                        );
                      }

                      if (/^\d+\.\s/.test(trimmed)) {
                        return (
                          <div key={idx} className="flex gap-2">
                            <span className="font-medium text-slate-600 shrink-0">
                              {trimmed.match(/^\d+\./)[0]}
                            </span>
                            <span>{trimmed.replace(/^\d+\.\s/, "")}</span>
                          </div>
                        );
                      }

                      if (/^```/.test(trimmed)) {
                        return (
                          <div
                            key={idx}
                            className="rounded-xl bg-zinc-900 text-white px-3 py-2 font-mono text-xs overflow-x-auto"
                          >
                            {trimmed.replace(/^```/, "")}
                          </div>
                        );
                      }

                      return (
                        <p key={idx} className="whitespace-pre-wrap">
                          {line}
                        </p>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex-1">
                    <ResponseRenderer mode={msg.mode} data={msg.data} />
                  </div>
                )}
              </div>
            );
          })}

          {state.loading && (
            <div className="flex gap-3 justify-start">
              <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center shrink-0 mt-1">
                <Bot size={16} />
              </div>
              <div className="max-w-[85%] rounded-2xl bg-slate-50 border border-slate-200 px-4 py-3 shadow-sm">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className="h-2 w-2 rounded-full bg-slate-400 animate-pulse" />
                  Thinking...
                </div>
              </div>
            </div>
          )}

          {state.error && <ResponseRenderer error={state.error} />}

          <div ref={bottomRef} />
        </div>
      </div>

      <hr />

      <div className="p-4 bg-white w-full">
        <div className="max-w-3xl mx-auto flex gap-2 items-end">
          <textarea
            value={state.query}
            onChange={(e) =>
              dispatch({ type: "SET_QUERY", payload: e.target.value })
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask something..."
            rows={1}
            className="flex-1 resize-none border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black/20 min-w-5/6"
          />

          <button
            onClick={sendMessage}
            disabled={state.loading}
            className="h-10 w-10 flex items-center justify-center rounded-xl bg-black text-white hover:bg-gray-800 disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;