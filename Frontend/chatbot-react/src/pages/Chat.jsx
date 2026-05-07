import { useState } from "react";
import "../App.css";
import { enviarMensaje } from "../api";
import buho from "../assets/buho_logo.png";

/**
 * Componente principal del chat.
 *
 * Este componente administra:
 * - El estado del mensaje escrito por el usuario.
 * - El historial de mensajes entre usuario y bot.
 * - El indicador visual de respuesta en proceso.
 * - La apertura y cierre del sidebar.
 */
function Chat() {
  /**
   * Almacena el texto actual escrito en el input.
   */
  const [mensaje, setMensaje] = useState("");

  /**
   * Almacena la conversación completa.
   *
   * Cada elemento del arreglo representa un mensaje con la siguiente estructura:
   * {
   *   autor: "usuario" | "bot",
   *   texto: string
   * }
   */
  const [mensajes, setMensajes] = useState([]);

  /**
   * Indica si el bot se encuentra generando una respuesta.
   * Se utiliza para mostrar el indicador de escritura.
   */
  const [escribiendo, setEscribiendo] = useState(false);

  /**
   * Controla el estado visual del sidebar.
   *
   * true  -> sidebar abierto
   * false -> sidebar cerrado
   */
  const [sidebarAbierto, setSidebarAbierto] = useState(true);

  /**
   * Preguntas predefinidas que se muestran en la pantalla inicial.
   * Permiten al usuario iniciar una conversación rápidamente.
   */
  const preguntasRapidas = [
    "¿Cuáles son los requisitos para tener un psicologo?",
    "¿Cómo solicito una constancia?",
    "¿Cuáles son los horarios de atención?",
    "¿Cómo hago un trámite de beca?",
  ];

  /**
   * Envía un mensaje al backend y actualiza la conversación.
   *
   * @param {string} texto - Mensaje opcional. Se usa principalmente
   * para enviar preguntas rápidas sin depender del valor del input.
   */
  const enviar = async (texto) => {
    const msg = texto || mensaje;

    // Evita enviar mensajes vacíos o compuestos únicamente por espacios.
    if (!msg.trim()) return;

    // Agrega el mensaje del usuario al historial de conversación.
    setMensajes((prev) => [
      ...prev,
      {
        autor: "usuario",
        texto: msg,
      },
    ]);

    // Limpia el input después de enviar el mensaje.
    setMensaje("");

    // Activa el indicador de escritura mientras se espera la respuesta.
    setEscribiendo(true);

    try {
      // Envía el mensaje al backend y espera la respuesta del bot.
      const respuesta = await enviarMensaje(msg);

      // Agrega la respuesta del bot al historial de conversación.
      setMensajes((prev) => [
        ...prev,
        {
          autor: "bot",
          texto: respuesta,
        },
      ]);
    } catch (error) {
      // Registra errores para facilitar la depuración durante el desarrollo.
      console.error(error);
    } finally {
      // Desactiva el indicador de escritura al finalizar la petición.
      setEscribiendo(false);
    }
  };

  return (
    <div className={`parent ${sidebarAbierto ? "sidebar-open" : "sidebar-closed"}`}>
      {/* =====================================================
          SIDEBAR
          Contiene accesos rápidos y el botón para contraer
          o expandir el menú lateral.
      ===================================================== */}
      <div className={`div1 ${sidebarAbierto ? "abierto" : "cerrado"}`}>
        <button
          className="toggle-btn"
          onClick={() => setSidebarAbierto(!sidebarAbierto)}
        >
          {sidebarAbierto ? "✕" : "☰"}
        </button>

        {/* El contenido del sidebar solo se renderiza cuando está abierto. */}
        {sidebarAbierto && (
          <div className="sidebar-contenido">
            <h3 className="sidebar-titulo">Acceso rápido</h3>

            <ul className="sidebar-lista">
              <li> Documentos</li>
              <li> Preguntas frecuentes</li>
              <li> Horarios</li>
              <li> Contacto</li>
              <li> Avisos</li> 
            </ul>
          </div>
        )}
      </div>

      {/* =====================================================
          COLUMNA PRINCIPAL DEL CHAT
          Incluye navbar, área de mensajes e input.
      ===================================================== */}
      <div className="columna-derecha">
        {/* =====================================================
            NAVBAR DEL CHAT
        ===================================================== */}
        <div className="chat-navbar">
          <span className="chat-titulo">ChatBuho</span>

          <button className="btn-compartir">
            ↑ Compartir
          </button>
        </div>

        {/* =====================================================
            ÁREA DE MENSAJES
            Muestra la bienvenida, los mensajes y el indicador
            de escritura del bot.
        ===================================================== */}
        <div className="div2">
          <div className="chat-box">
            {/* Pantalla inicial. Se muestra solo cuando no existe conversación activa. */}
            {mensajes.length === 0 && !escribiendo && (
              <div className="bienvenida">
                <img src={buho} alt="Logo de ChatBuho" className="buho-bienvenida" />

                <h2 className="glow-text">¡Hola! Soy ChatBuho</h2>
                <p>¿En qué puedo ayudarte hoy?</p>

                {/* Botones para iniciar una conversación con preguntas frecuentes. */}
                <div className="preguntas-rapidas">
                  {preguntasRapidas.map((p, i) => (
                    <button
                      key={i}
                      className="pregunta-btn"
                      onClick={() => enviar(p)}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Renderizado del historial de mensajes. */}
            {mensajes.map((m, i) => (
              <div key={i} className={`mensaje-wrapper ${m.autor}`}>
                {/* El avatar únicamente se muestra en los mensajes del bot. */}
                {m.autor === "bot" && (
                  <img src={buho} alt="Avatar de ChatBuho" className="avatar" />
                )}

                <div className={`mensaje ${m.autor}`}>
                  {m.texto}
                </div>
              </div>
            ))}

            {/* Indicador visual mientras se espera la respuesta del bot. */}
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

        {/* =====================================================
            INPUT DEL CHAT
            Permite escribir y enviar mensajes al bot.
        ===================================================== */}
        <div className="div3">
          <div className="input-wrapper">
            <input
              className="input-chat"
              value={mensaje}
              onChange={(e) => setMensaje(e.target.value)}
              placeholder="Escribe tu mensaje..."
              onKeyDown={(e) => e.key === "Enter" && enviar()}
            />

            <button
              className="button"
              onClick={() => enviar()}
              disabled={escribiendo}
            >
              Enviar
            </button>
          </div>

          {/* Aviso informativo sobre posibles errores en respuestas generadas por IA. */}
          <p className="aviso-ia">
            ChatBuho es una IA y puede cometer errores. Verifica la información importante.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Chat;