import Image from "next/image";
import styles from "./page.module.css";

import Searchbar from "@/components/SearchBar";

export default function Home() {
	return (
		<div className={styles.page}>
			<main className={styles.main}>
				<div className={styles.searchBar}>
					<Searchbar></Searchbar>
				</div>
			</main>
		</div>
	);
}
