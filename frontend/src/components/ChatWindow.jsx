import React, { useRef, useEffect, useReducer } from "react";
import { Send, Bot, User, ArrowRight } from "lucide-react";
import UploadPanel from "./UploadPanel.jsx";
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
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
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
     
      const { data } = await axios.post(`${backendUrl}/chat/model` , payload);
      console.log(data);

      dispatch({ type: "SET_RESPONSE", payload: data });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data?.response || "No response received." },
      ]);
    } catch (err) {
      dispatch({
        type: "SET_ERROR",
        payload: err?.message || "Something went wrong",
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
        <div className="max-w-2xl mx-auto space-y-6">
          {messages.map((msg, i) => (
            <div key={i} className="flex gap-3">
              <div className="h-8 w-8 rounded-full flex items-center justify-center bg-gray-200">
                {msg.role === "user" ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                {msg.text}
              </div>
            </div>
          ))}

          {state.loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="text-gray-500 text-sm">Thinking...</div>
            </div>
          )}

          {state.error && (
            <div className="text-sm text-red-600">{state.error}</div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <hr />

      <div className="p-4 bg-white w-full">
        <div className="max-w-2xl mx-auto flex gap-2 items-end">
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
            className="h-10 w-10 flex items-center justify-center rounded-xl bg-black text-white hover:bg-gray-800"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;