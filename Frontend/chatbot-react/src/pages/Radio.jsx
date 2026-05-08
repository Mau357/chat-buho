import styled from 'styled-components';

const Radio = ({ onChange, disabled }) => {
  const handleChange = (valor) => {
    if (disabled) return;
    // Espera 800ms para que se vea la animación antes de enviar
    setTimeout(() => {
      if (onChange) onChange(valor);
    }, 800);
  };

  return (
    <StyledWrapper>
      <div className="rating">
        <input type="radio" id="star-5" name="star-radio" value="5" onChange={() => handleChange(5)} disabled={disabled} />
        <label htmlFor="star-5">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path pathLength={360} d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z" /></svg>
        </label>
        <input type="radio" id="star-4" name="star-radio" value="4" onChange={() => handleChange(4)} disabled={disabled} />
        <label htmlFor="star-4">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path pathLength={360} d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z" /></svg>
        </label>
        <input type="radio" id="star-3" name="star-radio" value="3" onChange={() => handleChange(3)} disabled={disabled} />
        <label htmlFor="star-3">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path pathLength={360} d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z" /></svg>
        </label>
        <input type="radio" id="star-2" name="star-radio" value="2" onChange={() => handleChange(2)} disabled={disabled} />
        <label htmlFor="star-2">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path pathLength={360} d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z" /></svg>
        </label>
        <input type="radio" id="star-1" name="star-radio" value="1" onChange={() => handleChange(1)} disabled={disabled} />
        <label htmlFor="star-1">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path pathLength={360} d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.45,13.97L5.82,21L12,17.27Z" /></svg>
        </label>
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  .rating {
    display: flex;
    flex-direction: row-reverse;
    justify-content: flex-end;
    gap: 0.3rem;
    --stroke: #666;
    --fill: #ffc73a;
  }
  .rating input {
    appearance: unset;
  }
  .rating label {
    cursor: pointer;
  }
  .rating svg {
    width: 1.2rem;
    height: 1.2rem;
    overflow: visible;
    fill: transparent;
    stroke: var(--stroke);
    stroke-linejoin: bevel;
    stroke-dasharray: 12;
    animation: idle 4s linear infinite;
    transition: stroke 0.2s, fill 0.5s;
  }
  @keyframes idle {
    from { stroke-dashoffset: 24; }
  }
  .rating label:hover svg {
    stroke: var(--fill);
  }
  .rating input:checked ~ label svg {
    transition: 0s;
    animation: idle 4s linear infinite, yippee 0.75s backwards;
    fill: var(--fill);
    stroke: var(--fill);
    stroke-opacity: 0;
    stroke-dasharray: 0;
    stroke-linejoin: miter;
    stroke-width: 8px;
  }
  @keyframes yippee {
    0% {
      transform: scale(1);
      fill: var(--fill);
      fill-opacity: 0;
      stroke-opacity: 1;
      stroke: var(--stroke);
      stroke-dasharray: 10;
      stroke-width: 1px;
      stroke-linejoin: bevel;
    }
    30% {
      transform: scale(0);
      fill: var(--fill);
      fill-opacity: 0;
      stroke-opacity: 1;
      stroke: var(--stroke);
      stroke-dasharray: 10;
      stroke-width: 1px;
      stroke-linejoin: bevel;
    }
    30.1% {
      stroke: var(--fill);
      stroke-dasharray: 0;
      stroke-linejoin: miter;
      stroke-width: 8px;
    }
    60% {
      transform: scale(1.2);
      fill: var(--fill);
    }
  }
`;

export default Radio;
