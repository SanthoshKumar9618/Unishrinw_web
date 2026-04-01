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

export default function DemoCallPage() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const [status, setStatus] = useState<Status>("idle");
  const [config, setConfig] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [leadId, setLeadId] = useState<string | null>(null);

  const MAX_RECORD_TIME = 6000;

  // =============================
  // INIT
  // =============================
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

  // =============================
  // START CALL
  // =============================
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

      await playAudio(data?.data?.audio_url);

      startRecording();

    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  // =============================
  // RECORD
  // =============================
  const startRecording = async () => {
    if (status === "ended") return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1,
            sampleRate: 48000,
          },
        });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm", // 🔥 FIXED
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

  // =============================
  // SEND AUDIO
  // =============================
  const sendAudio = async () => {
    if (!config || !sessionId) return;

    setStatus("processing");

    try {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      console.log("BLOB SIZE:", blob.size);

      // 🔥 DEBUG — hear what you recorded
      const debugAudio = new Audio(URL.createObjectURL(blob));
      debugAudio.controls = true;
      document.body.appendChild(debugAudio);

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

      await playAudio(data?.data?.audio_url);

      startRecording();

    } catch (err) {
      console.error(err);
      setStatus("idle");
    }
  };

  // =============================
  // AUDIO
  // =============================
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
      console.error("Audio failed", err);
      setStatus("error");
    }
  };

  // =============================
  // END
  // =============================
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
    <div className="min-h-screen flex items-center justify-center bg-black text-white">
      <div className="space-y-4 text-center">

        <h1 className="text-2xl">AI Voice Call</h1>

        <p>{status}</p>

        {status === "idle" && (
          <button
            onClick={startCall}
            className="bg-blue-600 px-6 py-3 rounded-xl"
          >
            Start Call
          </button>
        )}

        <button
          onClick={handleEnd}
          className="bg-red-600 px-6 py-3 rounded-xl"
        >
          End Call
        </button>

      </div>
    </div>
  );
}