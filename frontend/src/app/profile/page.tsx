import styles from "./page.module.css";
import Image from "next/image";

export default async function profilePage({
	searchParams,
}: {
	searchParams: Promise<{ gameName: string; tagLine: string }>;
}) {
	const { gameName, tagLine } = await searchParams;

	const res = await fetch(`http://localhost:8000/player/${gameName}/${tagLine}`);
	if (!res.ok) {
		return <h1>Player not found</h1>;
	}
	const data = await res.json();
	console.log(data.top_mastery[0]);

	return (
		<div className={styles.container}>
			<div className={styles.leftSide}>
				<div className={styles.profileInfos}>
					<Image
						src={
							"http://localhost:8000/static/profileicon/" +
							data.summoner.profileIconId +
							".png"
						}
						alt="profile"
						width={100}
						height={100}
						priority={true}
					/>
					<h3>{data.player.gameName}</h3>
					<h4>{data.player.tagLine}</h4>
				</div>
				<div className={styles.champsList}></div>
			</div>
			<div className={styles.rightSide}>
				<div className={styles.mostPlayedChamps}>
					{data.top_mastery.map(champs => (
						<li key={champs["championId"]}>
							<Image
								src={
									"http://localhost:8000/static/champion/" +
									champs["championName"] +
									".png"
								}
								alt="champ pp"
								width={100}
								height={100}
								priority={true}
							/>
						</li>
					))}
				</div>
				<div className={styles.matchsHistory}></div>
			</div>
		</div>
	);
}
