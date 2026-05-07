import "./Inicio.css";
import itesiLogo from '../assets/ITESI_h23.png';
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import LoadingScreen from "./LoadingScreen";

function Inicio () {

const navigate = useNavigate();
 const [cargando, setCargando] = useState(false);

 if (cargando) {
    return <LoadingScreen onFinish={() => navigate("/chat")} />;
  }

  return (
    <div className="hero">

      <nav className="navbar">
        <img src={itesiLogo} alt="logo" className="imagenLogo" />
        
        <div className="nav-links">
          <button 
            className="btn2"
            onClick={() => navigate("/politicas")}
          >
            <span className="spn2">Politicas y condiciones</span>
          </button>

          <button className="btn2"><span className="spn2">Acerca de nosotros</span></button>
        </div>

        <div className="nav-actions">
          <button className="quejas" data-text="SUGERENCIAS">
            <i>Q</i>
            <i>U</i>
            <i>E</i>
            <i>J</i>
            <i>A</i>
            <i>S</i>
          </button>
        </div>
      </nav>

      <div className="hero-content">

        <div className="hero-text">
          <h1>
            Chat <span> Buho</span> 
          </h1>

          <p>
            Tienes dudas? <span>ChatBuho</span> te las resuelve
          </p>

          <button className="cta" onClick={() => setCargando(true)}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12h15m0 0l-6.75-6.75M19.5 12l-6.75 6.75" />
            </svg>

            <span className="text">Comenzar</span>
          </button>

        </div>

      </div>
    </div>
  );
}

export default Inicio;