"use client";

import { useEffect, useRef, useState } from "react";
import { processVoice, endSession } from "@/lib/api/voice";

type Status =
  | "idle"
  | "connecting"
  | "listening"
  | "processing"
  | "speaking"
  | "ended"
  | "error";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function DemoCallPage() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const [status, setStatus] = useState<Status>("idle");
  const [config, setConfig] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [leadId, setLeadId] = useState<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([]);

  const MAX_RECORD_TIME = 6000;

  useEffect(() => {
    const cfg = localStorage.getItem("voice_config");
    const sid = localStorage.getItem("session_id");
    const lid = localStorage.getItem("lead_id");

    if (!cfg || !sid) {
      alert("Missing config");
      window.location.href = "/";
      return;
    }

    setConfig(JSON.parse(cfg));
    setSessionId(sid);
    setLeadId(lid);
  }, []);

  const startCall = async () => {
    if (!config || !sessionId) return;

    setStatus("connecting");

    try {
      const formData = new FormData();

      formData.append("request_id", crypto.randomUUID());
      formData.append("audio", new Blob([], { type: "audio/webm" }));
      formData.append("session_id", sessionId);
      formData.append("persona", config.persona);
      formData.append("prompt", config.prompt);
      formData.append("language", config.language);
      formData.append("voice", config.voice);

      const data = await processVoice(formData);

      const aiText = data?.data?.text || "Hello 👋";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: aiText },
      ]);

      await playAudio(data?.data?.audio_url);

      startRecording();
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  const startRecording = async () => {
    if (status === "ended") return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.onstop = sendAudio;

      recorder.start();
      setStatus("listening");

      setTimeout(() => recorder.stop(), MAX_RECORD_TIME);
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  const sendAudio = async () => {
    if (!config || !sessionId) return;

    setStatus("processing");

    try {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });

      if (blob.size < 2000) {
        return startRecording();
      }

      const formData = new FormData();

      formData.append("request_id", crypto.randomUUID());
      formData.append("audio", blob);
      formData.append("session_id", sessionId);
      formData.append("persona", config.persona);
      formData.append("prompt", config.prompt);
      formData.append("language", config.language);
      formData.append("voice", config.voice);

      const data = await processVoice(formData);

      const userText = data?.data?.user_text || "...";
      const aiText = data?.data?.text || "...";

      setMessages((prev) => [
        ...prev,
        { role: "user", content: userText },
        { role: "assistant", content: aiText },
      ]);

      await playAudio(data?.data?.audio_url);

      startRecording();
    } catch (err) {
      console.error(err);
      setStatus("idle");
    }
  };

  const playAudio = async (url: string) => {
    setStatus("speaking");

    try {
      const audio = new Audio(url + "&t=" + Date.now());
      audioRef.current = audio;

      await audio.play();

      return new Promise<void>((resolve) => {
        audio.onended = () => {
          setStatus("idle");
          resolve();
        };
      });
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  const handleEnd = async () => {
    setStatus("ended");

    mediaRecorderRef.current?.stop();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    audioRef.current?.pause();

    await endSession({
      session_id: sessionId,
      lead_id: leadId,
    });

    window.location.href = "/";
  };

  return (
  <div className="h-screen flex items-center justify-center bg-white">

    {/* MAIN CONTAINER */}
    <div className="flex gap-12 items-center">

      {/* ================= LEFT: PHONE ================= */}
      <div className="w-[260px] h-[500px] rounded-[40px] bg-[#1e293b] shadow-xl flex flex-col items-center justify-center">

        {/* Avatar */}
        <div className="w-20 h-20 rounded-full bg-[#334155] flex items-center justify-center text-2xl text-white">
          🤖
        </div>

        {/* Status */}
        <p className="mt-6 text-sm text-gray-300">
          {status === "connecting" && "Calling..."}
          {status === "listening" && "Listening..."}
          {status === "processing" && "Thinking..."}
          {status === "speaking" && "Speaking..."}
          {status === "idle" && "Ready"}
        </p>

        {/* Buttons */}
        <div className="flex gap-4 mt-10">
          {status === "idle" && (
            <button
              onClick={startCall}
              className="w-12 h-12 rounded-full bg-green-500 text-white"
            >
              📞
            </button>
          )}

          <button
            onClick={handleEnd}
            className="w-12 h-12 rounded-full bg-red-500 text-white"
          >
            ✕
          </button>
        </div>
      </div>

      {/* ================= RIGHT: CHAT ================= */}
      <div className="w-[320px] h-[500px] rounded-[30px] bg-white/70 backdrop-blur-md border border-gray-200 shadow-lg flex flex-col overflow-hidden">

        {/* Header */}
        <div className="p-3 text-center text-sm font-medium text-gray-600 border-b">
          Conversation
        </div>

        {/* Chat Area */}
        <div className="flex-1 p-3 space-y-2 overflow-y-auto bg-gray-50">

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`
                  px-3 py-2 text-sm rounded-lg max-w-[75%]
                  ${
                    msg.role === "user"
                      ? "bg-blue-500 text-white rounded-br-none"
                      : "bg-gray-200 text-black rounded-bl-none"
                  }
                `}
              >
                {msg.content}
              </div>
            </div>
          ))}

        </div>

      </div>

    </div>
  </div>
);
}