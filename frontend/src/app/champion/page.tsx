import React from "react";

import styles from "./page.module.css";

export default async function ChampionPage({
	searchParams,
}: {
	searchParams: Promise<{ puuid: string, id: string }>;
}) {
	const { puuid, id } = await searchParams;
	const res = await fetch(`http://localhost:8000/champion-stats/${puuid}/${id}`);
	if (!res.ok) {
		return <h1>Failed to fetch champion stats</h1>
	}
	const data = await res.json();
	console.log(data);

	const backgroundImageId = data[0]["participant.championIdString"];
	const backgroundImageUrl = `http://localhost:8000/img/champion/splash/${backgroundImageId}_0.jpg`;

	return (
		<div className={styles.container}
			style={{
				"--backgroundImageUrl": `url(${backgroundImageUrl})`,
			} as React.CSSProperties}
		>
			<h1>Champion Page</h1>
		</div>
	);
}