import styles from "../styles/AppFooter.module.css";

export default function AppFooter() {
  return (
    <footer className={styles.footer}>
      <span className={styles.ripples} aria-hidden="true">
        <span />
        <span />
        <span />
      </span>
      <span className={styles.brand}>
        Du<span className={styles.brandAccent}>ack</span>
        <span className={styles.brandBang}>!</span>
      </span>
    </footer>
  );
}