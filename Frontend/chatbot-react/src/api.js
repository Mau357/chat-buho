export async function enviarMensaje(texto) {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data;  // ← único cambio
}
export const calificarRespuesta = async (id_monitoreo, util) => {
    const response = await fetch("http://localhost:8000/chat/calificar", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_monitoreo, util })  // util ya será 1-5
    });
    return response.json();
};