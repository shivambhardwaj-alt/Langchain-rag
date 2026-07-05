import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const newMessages = [...messages, { role: "user", text }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "This is a response from AI backend.",
        },
      ]);
      setLoading(false);
    }, 800);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white  w-full p-3">

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
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

          {loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="text-gray-500 text-sm">Thinking...</div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

  
          <hr />
      <div className=" p-4 bg-white w-full">
        <div className="max-w-2xl mx-auto flex gap-2 items-end">

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
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