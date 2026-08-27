import { useState } from "react";
import styles from "../styles/DuckButton.module.css";
import useQuackSound from "../hooks/useQuackSound";

interface DuckButtonProps {
  onQuack: () => void;
}

const INK = "#2B1710";
const BODY = "#FFDE59";
const BEAK = "#F2A93B";

export default function DuckButton({ onQuack }: DuckButtonProps) {
  const [pressed, setPressed] = useState(false);
  const playQuack = useQuackSound();

  function handleClick() {
    playQuack();
    onQuack();
    setPressed(true);
    window.setTimeout(() => setPressed(false), 150);
  }

  return (
    <button
      type="button"
      className={`${styles.duckButton} ${pressed ? styles.pressed : ""}`}
      onClick={handleClick}
      aria-label="Haz click en el pato para sumar un cuak"
    >
      <svg
        viewBox="0 0 240 270"
        className={styles.duckSvg}
        role="img"
        aria-hidden="true"
      >
        {/* sombra de contacto */}
        <ellipse cx="120" cy="260" rx="66" ry="9" fill="rgba(0,0,0,0.18)" />

        {/* patas: contorno + relleno, dibujadas antes del cuerpo para que asomen debajo */}
        <g transform="rotate(-12 90 248)">
          <ellipse cx="90" cy="248" rx="25" ry="16" fill={INK} />
          <ellipse cx="90" cy="248" rx="20" ry="12" fill={BEAK} />
        </g>
        <g transform="rotate(12 150 248)">
          <ellipse cx="150" cy="248" rx="25" ry="16" fill={INK} />
          <ellipse cx="150" cy="248" rx="20" ry="12" fill={BEAK} />
        </g>

        {/* silueta cuerpo + cabeza: capa de contorno (más grande, sin costuras) */}
        <ellipse cx="120" cy="165" rx="96" ry="82" fill={INK} />
        <circle cx="120" cy="78" r="64" fill={INK} />

        {/* silueta cuerpo + cabeza: capa de relleno amarillo encima */}
        <ellipse cx="120" cy="165" rx="90" ry="76" fill={BODY} />
        <circle cx="120" cy="78" r="58" fill={BODY} />

        {/* parche claro en la frente */}
        <ellipse cx="120" cy="54" rx="36" ry="17" fill="#FFF3C4" opacity="0.85" />

        {/* pico: contorno + relleno */}
        <ellipse cx="120" cy="99" rx="27" ry="15" fill={INK} />
        <ellipse cx="120" cy="98" rx="22" ry="12" fill={BEAK} />

        {/* ojitos simples */}
        <ellipse cx="94" cy="80" rx="7" ry="4" fill={INK} transform="rotate(-8 94 80)" />
        <ellipse cx="146" cy="80" rx="7" ry="4" fill={INK} transform="rotate(8 146 80)" />
      </svg>
    </button>
  );
}