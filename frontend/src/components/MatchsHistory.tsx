"use client";

import { useEffect, useState } from "react";
import { Matchs } from "@/app/profile/page";

import styles from "./MatchsHistory.module.css";
import Image from "next/image";

export default function MatchsHistory({ puuid }: { puuid: string }) {
	const [pageNumber, setPageNumber] = useState<number>(1);
	const [matchsList, setMatchsList] = useState<Matchs[]>([]);
	const [isLastPage, setIsLastPage] = useState<boolean>(false);

	useEffect(() => {
		fetch(`http://localhost:8000/matchs/${puuid}?page=${pageNumber}`)
			.then(res => res.json())
			.then(data => {
				setMatchsList(data);
				if (data.length < 10) setIsLastPage(true);
				else setIsLastPage(false);
			});
	}, [puuid, pageNumber]);

	return (
		<div className={styles.matchsHistory}>
			{matchsList.map((match: Matchs) => (
				<li key={match["match.info.gameId"]}>
					<Image
						src={
							"http://localhost:8000/static/champion/" +
							match["participant.championIdString"] +
							".png"
						}
						alt="champ pp"
						width={30}
						height={30}
						priority={true}
					/>
					<p>{match["match.metadata.matchId"]}</p>
				</li>
			))}
			<button
				onClick={() => {
					if (pageNumber > 1) setPageNumber(pageNumber - 1);
				}}
			>
				<p>{"<"}</p>
			</button>
			<input
				type="number"
				value={pageNumber}
				onChange={e => setPageNumber(parseInt(e.target.value) || 1)}
			/>
			<button
				onClick={() => {
					if (!isLastPage) setPageNumber(pageNumber + 1);
				}}
			>
				<p>{">"}</p>
			</button>
		</div>
	);
}
