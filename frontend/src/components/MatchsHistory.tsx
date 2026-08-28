"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Matchs } from "@/app/profile/page";

import styles from "./MatchsHistory.module.css";
import Image from "next/image";

export default function MatchsHistory({ puuid }: { puuid: string }) {
	const [pageNumber, setPageNumber] = useState<number>(1);
	const [matchsList, setMatchsList] = useState<Matchs[]>([]);
	const [isLastPage, setIsLastPage] = useState<boolean>(false);
	const [errorMessage, setErrorMessage] = useState<string | null>(null);
	const [isLoading, setIsLoading] = useState<boolean>(false);

	const router = useRouter();

	useEffect(() => {
		setErrorMessage(null);
		setIsLoading(true);

		fetch(`http://localhost:8000/matchs/${puuid}?page=${pageNumber}`)
			.then(res => {
				if (!res.ok) {
					throw new Error("Error during matches loading");
				}
				return res.json();
			})
			.then(data => {
				setMatchsList(data);
				if (data.length < 10) setIsLastPage(true);
				else setIsLastPage(false);
			})
			.catch(error => {
				console.error("Error during matches loading", error);
				setErrorMessage("Can't load matches, please try again later.");
			})
			.finally(() => {
				setIsLoading(false);
			});
	}, [puuid, pageNumber]);

	return (
		<div>
			<div className={styles.matchsHistory}>
				{isLoading ? (
					<p>Chargement...</p>
				) : errorMessage ? (
					<p className={styles.error}>{errorMessage}</p>
				) : (
					matchsList.map((match: Matchs) => (
						<li key={match["match.info.gameId"]} className={styles.matchItem}
						onClick={() => router.push(`/match?id=${match["match.metadata.matchId"]}`)}>
							<Image
								src={
									"http://localhost:8000/static/champion/" +
									match["participant.championIdString"] +
									".png"
								}
								alt="champ pp"
								width={50}
								height={50}
								priority={true}
							/>
							<p>{match["match.metadata.matchId"]}</p>
						</li>
					))
				)}
			</div>
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
				className={styles.pageInput}
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