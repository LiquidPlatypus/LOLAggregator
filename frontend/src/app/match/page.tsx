import { Matchs } from "@/app/profile/page";
import Image from "next/image";

import styles from "./page.module.css";

export default async function MatchPage({
	searchParams,
}: {
	searchParams: Promise<{ id?: string }>;
}) {
	const { id } = await searchParams;
	if (!id) {
		return <h1>Match ID missing</h1>;
	}
	const res = await fetch(`http://localhost:8000/match/${id}`);
	if (!res.ok) {
		return <h1>Match not found</h1>;
	}
	const data = (await res.json()) as Matchs;
	console.log(data.info)

	return (
		<div>
			<ul className={styles.champsTab}>
				{data.info.participants.map((participant) => (
					<li key={participant.puuid} className={styles.champTab}>
						<Image
							src={
								"http://localhost:8000/static/champion/" +
								participant.championName +
								".png"
							}
							alt={participant.championName}
							width={50}
							height={50}
						/>
						<h3>{participant.kills}/{participant.deaths}/{participant.assists}</h3>
					</li>
				))}
			</ul>

		</div>
	);
}
