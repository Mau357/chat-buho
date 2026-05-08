import { useState } from "react";
import "../App.css";
import { enviarMensaje, calificarRespuesta } from "../api";
import buho from "../assets/buho_logo.png";
import Radio from "./Radio";

function Chat() {
  const [mensaje, setMensaje] = useState("");
  const [mensajes, setMensajes] = useState([]);
  const [escribiendo, setEscribiendo] = useState(false);
  const [sidebarAbierto, setSidebarAbierto] = useState(false);
const [temaActivo, setTemaActivo] = useState('dark');

  const preguntasRapidas = [
    "¿Cuáles son los requisitos para tener un psicólogo?",
    "¿Cómo solicito una constancia?",
    "¿Cuáles son los horarios de atención?",
    "¿Cómo hago un trámite de beca?",
  ];

  const enviar = async (texto) => {
    const msg = texto || mensaje;
    if (!msg.trim()) return;

    setMensajes((prev) => [...prev, { autor: "usuario", texto: msg }]);
    setMensaje("");
    setEscribiendo(true);

    try {
      const data = await enviarMensaje(msg);

      setMensajes((prev) => [
        ...prev,
        {
          autor: "bot",
          texto: data.respuesta,
          id_monitoreo: data.id_monitoreo,
          calificado: null,
        },
      ]);
    } catch (error) {
      console.error(error);
    } finally {
      setEscribiendo(false);
    }
  };

  const calificar = async (id_monitoreo, valor, index) => {
    if (!id_monitoreo) return;
    await calificarRespuesta(id_monitoreo, valor);
    setMensajes((prev) =>
      prev.map((m, i) => (i === index ? { ...m, calificado: valor } : m))
    );
  };

  return (
    <div className={`parent ${sidebarAbierto ? "sidebar-open" : "sidebar-closed"}`}>
      {/* SIDEBAR */}
      <div
  className={`div1 ${sidebarAbierto ? "abierto" : "cerrado"}`}
  onMouseEnter={() => setSidebarAbierto(true)}
  onMouseLeave={() => setSidebarAbierto(false)}
>
  {/* Ícono hamburguesa — solo visible cuando está cerrado */}
  {!sidebarAbierto && (
    <div className="hamburguesa">
      <span></span>
      <span></span>
      <span></span>
    </div>
  )}

 {sidebarAbierto && (
  <div className="sidebar-contenido">
    <div className="temas">
      <button className={`tema-btn ${temaActivo === 'light' ? 'activo' : ''}`} onClick={() => setTemaActivo('light')}>☀︎ Light</button>
      <button className={`tema-btn ${temaActivo === 'dark' ? 'activo' : ''}`} onClick={() => setTemaActivo('dark')}>❄︎ Dark</button>
      <button className={`tema-btn ${temaActivo === 'black' ? 'activo' : ''}`} onClick={() => setTemaActivo('black')}>☁︎ Black</button>
    </div>

    <ul className="sidebar-lista">
      <li>Documentos</li>
      <li>Preguntas frecuentes</li>
      <li>Horarios</li>
      <li>Contacto</li>
      <li>Avisos</li>
    </ul>
  </div>
)}
</div>
     
      
   

      <div className="columna-derecha">
        <div className="chat-navbar">
          <span className="chat-titulo">ChatBuho</span>
          <button className="btn-compartir">↑ Compartir</button>
        </div>

        <div className="div2">
          <div className="chat-box">
            {/* Pantalla de bienvenida */}
            {mensajes.length === 0 && !escribiendo && (
              <div className="bienvenida">
                <img src={buho} alt="Logo de ChatBuho" className="buho-bienvenida" />
                <h2 className="glow-text">¡Hola! Soy ChatBuho</h2>
                <p>¿En qué puedo ayudarte hoy?</p>
                <div className="preguntas-rapidas">
                  {preguntasRapidas.map((p, i) => (
                    <button key={i} className="pregunta-btn" onClick={() => enviar(p)}>
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Historial de mensajes */}
            {mensajes.map((m, i) => (
              <div key={i} className={`mensaje-wrapper ${m.autor}`}>
                {m.autor === "bot" && (
                  <img src={buho} alt="Avatar de ChatBuho" className="avatar" />
                )}

                <div className="mensaje-bloque">
                  <div className={`mensaje ${m.autor}`}>{m.texto}</div>

                  {/* Calificación — solo en mensajes del bot con id_monitoreo */}
                  {m.autor === "bot" && m.id_monitoreo && (
                    <div className="calificacion">
                      {m.calificado === null ? (
                        <Radio
                          onChange={(valor) => calificar(m.id_monitoreo, valor, i)}
                        />
                      ) : (
                        <span className="calificacion-enviada">
                          ¡Gracias por tu calificacion, el búho lo revisara! 🦉
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Indicador de escritura */}
            {escribiendo && (
              <div className="mensaje-wrapper bot">
                <img src={buho} alt="Avatar de ChatBuho" className="avatar" />
                <div className="mensaje bot escribiendo">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="div3">
          <div className="input-wrapper">
            <input
              className="input-chat"
              value={mensaje}
              onChange={(e) => setMensaje(e.target.value)}
              placeholder="Escribe tu mensaje..."
              onKeyDown={(e) => e.key === "Enter" && enviar()}
            />
            <button className="button" onClick={() => enviar()} disabled={escribiendo}>
              Enviar
            </button>
          </div>
          <p className="aviso-ia">
            ChatBuho es una IA y puede cometer errores. Verifica la información importante.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Chat;
