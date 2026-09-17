import styles from "./Footer.module.css";

export default function Footer() {
	return (
		<div className={styles.footer}>
			<p>LOLAggregator &copy; {new Date().getFullYear()}</p>
		</div>
	);
}
