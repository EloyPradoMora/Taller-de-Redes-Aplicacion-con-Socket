import { useEffect, useRef, useState } from "react";
import styles from "../styles/ClickerPage.module.css";
import DuckButton from "../components/DuckButton";
import AppFooter from "../components/AppFooter";

const STORAGE_KEY = "cuak-clicker-record";

interface Quack {
  id: number;
  x: number;
  rotation: number;
}

interface Ripple {
  id: number;
}

function loadRecord(): number {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  const parsed = raw ? Number.parseInt(raw, 10) : 0;
  return Number.isFinite(parsed) ? parsed : 0;
}

export default function ClickerPage() {
  const [clicks, setClicks] = useState(0);
  const [record, setRecord] = useState<number>(() => loadRecord());
  const [justBeatRecord, setJustBeatRecord] = useState(false);
  const [quacks, setQuacks] = useState<Quack[]>([]);
  const [ripples, setRipples] = useState<Ripple[]>([]);
  const nextId = useRef(0);

  useEffect(() => {
    if (clicks > record) {
      setRecord(clicks);
      window.localStorage.setItem(STORAGE_KEY, String(clicks));
      setJustBeatRecord(true);
      const timeout = setTimeout(() => setJustBeatRecord(false), 700);
      return () => clearTimeout(timeout);
    }
  }, [clicks, record]);

  function handleQuack() {
    setClicks((current) => current + 1);

    const id = nextId.current++;
    const quack: Quack = {
      id,
      x: Math.random() * 64 - 32,
      rotation: Math.random() * 16 - 8,
    };
    setQuacks((current) => [...current, quack]);
    window.setTimeout(() => {
      setQuacks((current) => current.filter((q) => q.id !== id));
    }, 900);

    const rippleId = nextId.current++;
    setRipples((current) => [...current, { id: rippleId }]);
    window.setTimeout(() => {
      setRipples((current) => current.filter((r) => r.id !== rippleId));
    }, 700);
  }

  return (
    <div className={styles.pond}>
      <div className={styles.topBar}>
        <div className={styles.counter}>
          <span className={styles.counterLabel}>Clicks</span>
          <span className={styles.counterValue}>{clicks}</span>
        </div>

        <div
          className={`${styles.recordChip} ${
            justBeatRecord ? styles.recordChipPulse : ""
          }`}
        >
          <span className={styles.recordLabel}>Récord</span>
          <span className={styles.recordValue}>{record}</span>
        </div>
      </div>

      <div className={styles.stage}>
        {ripples.map((ripple) => (
          <span key={ripple.id} className={styles.ripple} aria-hidden="true" />
        ))}

        {quacks.map((quack) => (
          <span
            key={quack.id}
            className={styles.quackBubble}
            style={{
              // @ts-expect-error CSS custom properties aren't in the type
              "--quack-x": `${quack.x}px`,
              "--quack-rotation": `${quack.rotation}deg`,
            }}
          >
            ¡Cuak!
          </span>
        ))}

        <DuckButton onQuack={handleQuack} />

        <div className={styles.lilyPad} aria-hidden="true" />
      </div>

      <AppFooter />
    </div>
  );
}