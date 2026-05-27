import './Inicio.css';
import itesiLogo from "../assets/ITESI_h23.png";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import LoadingScreen from "./LoadingScreen";

function Inicio() {
  const navigate = useNavigate();
  const [cargando, setCargando] = useState(false);

  if (cargando) {
    return <LoadingScreen onFinish={() => navigate("/chat")} />;
  }

  return (
    <div className="pagina-inicio">
      <header className="header">
        <img src={itesiLogo} alt="Logo ITESI" />
        <nav>
          <button onClick={() => navigate("/Politicas")}>POLÍTICAS Y CONDICIONES</button>
          <button onClick={() => navigate("/AcercaDe")}>ACERCA DE NOSOTROS</button>
          <button onClick={() => navigate("/Sugerencias")}>SUGERENCIAS</button>
        </nav>
      </header>

      <section className="hero">
        <div className="hero-texto">
          <h1>Chat Búho</h1>
          <p>¿Tienes dudas? ChatBúho te las resuelve</p>
          
            <button onClick={() => setCargando(true)}>
              Comenzar
            </button>
          
        </div>
      </section>
    </div>
  );
}

export default Inicio;