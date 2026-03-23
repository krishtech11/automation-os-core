import { useState } from "react";

function AIAssistant() {

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  const sendMessage = async () => {

    if (!message.trim()) return;

    const userMessage = message;

    setChat(prev => [...prev, { role: "user", text: userMessage }]);

    setMessage("");

    try {

      const res = await fetch("http://localhost:5000/api/assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await res.json();

      setChat(prev => [
        ...prev,
        {
          role: "assistant",
          text: data.reply
        }
      ]);

      // refresh dashboard tasks automatically
      window.dispatchEvent(new Event("refreshTasks"));

    } catch (err) {

      setChat(prev => [...prev, { role: "assistant", text: "Error contacting AI." }]);

    }
  };

  const startListening = () => {

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Voice recognition not supported in this browser.");
    return;
  }

  const recognition = new SpeechRecognition();

  recognition.lang = "en-US";
  recognition.interimResults = false;

  recognition.start();

  recognition.onresult = (event) => {

    const voiceText = event.results[0][0].transcript;

    setMessage(voiceText);

  };

};

  return (
    <div className="h-full flex flex-col bg-slate-950 text-white p-5">

      <h2 className="text-xl font-bold mb-4">UAOS AI</h2>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">

        {chat.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-xl max-w-[80%] ${
              msg.role === "user"
                ? "ml-auto bg-blue-600 text-white"
                : "bg-slate-800 text-slate-200"
            }`}
          >
            {msg.text}
          </div>
        ))}

      </div>

      {/* Input area */}
      <div className="flex gap-2 items-center">

        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask UAOS..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
        />

      <button
        onClick={startListening}
        className="bg-purple-600 hover:bg-purple-500 px-4 py-2 rounded-lg"
      >
      🎤
      </button>

      <button
        onClick={sendMessage}
        className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg font-semibold"
      >
      Send
      </button>

      </div>

    </div>
  );
}

export default AIAssistant;