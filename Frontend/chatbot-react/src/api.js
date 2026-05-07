
export async function enviarMensaje(texto) {
  const res = await fetch("http://localhost:8000/chat", { // <-- URL fija
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.respuesta;
}
