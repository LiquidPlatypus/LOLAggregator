"use client";

import React, {useEffect, useState} from "react";
import { useRouter } from "next/navigation";
import { PlayerResponse } from "@/app/profile/page";

import styles from "./SearchBar.module.css";
import Image from "next/image";

export default function Searchbar() {
	const [gameName, setGameName] = useState("");
	const [tagLine, setTagLine] = useState("");
	const [foundPlayer, setFoundPlayer] = useState<PlayerResponse | null>(null);
	const [isLoading, setIsLoading] = useState(false);

	const router = useRouter();

	useEffect(() => {
		if (!gameName || !tagLine) {
			setFoundPlayer(null);
			return;
		}

		const timerId = setTimeout(() => {
			setIsLoading(true);

			fetch(`http://localhost:8000/player/${gameName}/${tagLine}`)
				.then(res => {
					if (!res.ok) {
						throw new Error("Player not found");
					}
					return res.json();
				})
				.then(data => {
					setFoundPlayer(data);
				})
				.catch(() => {
					setFoundPlayer(null);
				})
				.finally(() => {
					setIsLoading(false);
				});
		}, 500);

		return () => clearTimeout(timerId);
	}, [gameName, tagLine]);

	return (
		<div>
			<form
				onSubmit={e => {
					e.preventDefault();
					router.push(`/profile?gameName=${gameName}&tagLine=${tagLine}`);
				}}
			>
				<input
					type="text"
					placeholder="Username"
					value={gameName}
					onChange={e => setGameName(e.target.value)}
					className={styles.gameNameInput}
				/>
				<input
					type="text"
					placeholder="Tagline"
					value={tagLine}
					onChange={e => setTagLine(e.target.value)}
					className={styles.tagLineInput}
				/>
			</form>
			{isLoading ? (
				<p>Loading...</p>
			) : foundPlayer ? (
				<div
					className={styles.playerCard}
					onClick={() => router.push(`/profile?gameName=${foundPlayer.player.gameName}&tagLine=${foundPlayer.player.tagLine}`)}
				>
					<Image
						src={
							"http://localhost:8000/static/profileicon/" +
							foundPlayer.summoner.profileIconId +
							".png"
						}
						alt="profile"
						width={50}
						height={50}
						priority={true}
					/>
					<h3>{foundPlayer.player.gameName}</h3>
					<h4>#{foundPlayer.player.tagLine}</h4>
				</div>
			) : null}
		</div>
	);
}
