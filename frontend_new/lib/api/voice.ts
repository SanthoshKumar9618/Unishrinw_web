const BASE_URL = "http://localhost:8000/api/v1";

export async function processVoice(formData: FormData) {
  const res = await fetch(`${BASE_URL}/process`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Process failed");

  return res.json();
}

export async function endSession(payload: {
  session_id: string | null;
  lead_id: string | null;
}) {
  const res = await fetch(`${BASE_URL}/end-session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) throw new Error("End session failed");

  return res.json();
}