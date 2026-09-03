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

	return (
		<div className={styles.matchContainer}>
			<ul className={styles.champsTab}>
				{data.match.info.participants.map((participant) => (
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
						<div className={styles.itemsContainer}>
							<ul className={styles.items}>
								{[
									participant.item0,
									participant.item1,
									participant.item2,
									participant.item3,
									participant.item4,
									participant.item5,
								].map((itemId, index) => {
									const item = itemId ? data.items[itemId] : null;

									return (
										<li key={item?.id ?? index} className={styles.item}>
											{item && (
												<Image
													src={`http://localhost:8000/static/item/${item.id}.png`}
													alt={item.name}
													width={30}
													height={30}
												/>
											)}
										</li>
									);
								})}
							</ul>
							<Image
								src={`http://localhost:8000/static/item/${participant.item6}.png`}
								alt="Item 6"
								width={30}
								height={30}
							/>
						</div>
					</li>
				))}
			</ul>

			<div className={styles.matchInfo}>
				<h1>{data.match.info.gameMode}</h1>
			</div>
		</div>
	);
}
