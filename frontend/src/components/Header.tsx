import Searchbar from "@/components/SearchBar";
import styles from "./Header.module.css";
import Link from "next/link";

export default function Header() {
	return (
		<header className={styles.header}>
			<div className={styles.hleftside}>
				<Link href="/">
					<h1>LOLAggregator</h1>
				</Link>
				<Searchbar />
			</div>
			<div>
				<button>Language</button>
			</div>
		</header>
	);
}
