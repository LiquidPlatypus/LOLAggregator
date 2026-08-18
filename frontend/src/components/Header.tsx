import Searchbar from "@/components/SearchBar";
import styles from "./Header.module.css";

export default function Header() {
	return (
		<header className={styles.header}>
			<div className={styles.hleftside}>
				<h1>LOLAggregator</h1>
				<Searchbar />
			</div>
			<div>
				<button>Language</button>
			</div>
		</header>
	);
}
