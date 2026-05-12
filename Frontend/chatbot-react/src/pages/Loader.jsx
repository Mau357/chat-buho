import React from "react";
import styled, { keyframes } from "styled-components";

const Loader = () => {
  return (
    <StyledWrapper>
      <div className="loader-wrapper">
        <span className="loader-letter">I</span>
        <span className="loader-letter">n</span>
        <span className="loader-letter">i</span>
        <span className="loader-letter">c</span>
        <span className="loader-letter">i</span>
        <span className="loader-letter">a</span>
        <span className="loader-letter">n</span>
        <span className="loader-letter">d</span>
        <span className="loader-letter">o</span>

        <div className="loader" />
      </div>
    </StyledWrapper>
  );
};

export default Loader;

/* ================= STYLES ================= */

const rotate = keyframes`
  0% {
    transform: rotate(90deg);
    box-shadow:
      0 10px 20px 0 #ffffff inset,
      0 20px 30px 0 #7c3aed inset,
      0 60px 60px 0 #312e81 inset;
  }
  50% {
    transform: rotate(270deg);
    box-shadow:
      0 10px 20px 0 #ffffff inset,
      0 20px 10px 0 #3b82f6 inset,
      0 40px 60px 0 #4c1d95 inset;
  }
  100% {
    transform: rotate(450deg);
    box-shadow:
      0 10px 20px 0 #ffffff inset,
      0 20px 30px 0 #8b5cf6 inset,
      0 60px 60px 0 #1e1b4b inset;
  }
`;

const letterAnim = keyframes`
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }

  20% {
    opacity: 1;
    color: #ffffff;
    text-shadow:
      0 0 10px rgba(139,92,246,0.9),
      0 0 20px rgba(59,130,246,0.5);
    transform: scale(1.15);
  }

  40% {
    opacity: 0.7;
    transform: scale(1);
  }
`;

const StyledWrapper = styled.div`
  width: 100vw;
  height: 100vh;

  display: flex;
  align-items: center;
  justify-content: center;

  background: radial-gradient(circle at top, #111827 0%, #000000 70%);
  font-family: "Poppins", sans-serif;
  overflow: hidden;

  .loader-wrapper {
    position: relative;
    width: 220px;
    height: 220px;

    display: flex;
    align-items: center;
    justify-content: center;

    color: white;
    font-size: 1.2em;
    font-weight: 500;
    user-select: none;
  }

  .loader {
    position: absolute;
    inset: 0;

    border-radius: 50%;
    animation: ${rotate} 2s linear infinite;
    z-index: 0;
  }

  .loader-letter {
    display: inline-block;
    opacity: 0.4;
    animation: ${letterAnim} 2s infinite ease-in-out;
    z-index: 1;
    letter-spacing: 1px;
  }

  .loader-letter:nth-child(1) { animation-delay: 0s; }
  .loader-letter:nth-child(2) { animation-delay: 0.1s; }
  .loader-letter:nth-child(3) { animation-delay: 0.2s; }
  .loader-letter:nth-child(4) { animation-delay: 0.3s; }
  .loader-letter:nth-child(5) { animation-delay: 0.4s; }
  .loader-letter:nth-child(6) { animation-delay: 0.5s; }
  .loader-letter:nth-child(7) { animation-delay: 0.6s; }
  .loader-letter:nth-child(8) { animation-delay: 0.7s; }
  .loader-letter:nth-child(9) { animation-delay: 0.8s; }
`;
