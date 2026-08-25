import MatchsHistory from "@/components/MatchsHistory";

import styles from "./page.module.css";
import Image from "next/image";

interface ChampionMastery {
	championName: string;
	championIdString: string;
	championId: number;
	championLevel: number;
	championPoints: number;
	lastPlayTime: string;
	championPointsSinceLastLevel: number;
	championPointsUntilNextLevel: number;
	markRequiredForNextLevel: number;
	tokensEarned: number;
	championSeasonMilestone: number;
	milestoneGrades: string[];
	"nextSeasonMilestone.requireGradeCounts.S-": number;
	"nextSeasonMilestone.rewardMarks": number;
	"nextSeasonMilestone.bonus": boolean;
	"nextSeasonMilestone.totalGamesRequires": number;
	"nextSeasonMilestone.requireGradeCounts.A-": number;
}

export interface Matchs {
	"match.info.gameId": number;
	"match.metadata.matchId": string;
	"participant.championIdString": string;
}

interface Player {
	puuid: string;
	gameName: string;
	tagLine: string;
}

interface Summoner {
	puuid: string;
	profileIconId: number;
	revisionDate: number;
	summonerLevel: number;
}

interface PlayerResponse {
	player: Player;
	summoner: Summoner;
	mastery: ChampionMastery[];
	top_mastery: ChampionMastery[];
	matchs_history: Matchs[];
}

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
	const data = (await res.json()) as PlayerResponse;

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
				<h2>All champs played</h2>
				<div className={styles.champsList}>
					{data.mastery
						.filter((champs: ChampionMastery) => champs.championName !== "Unknown")
						.map((champs: ChampionMastery) => (
							<li className={styles.champListli} key={champs.championId}>
								<Image
									src={
										"http://localhost:8000/static/champion/" +
										champs["championIdString"] +
										".png"
									}
									alt="champ"
									width={50}
									height={50}
									priority={true}
								/>
								<h3>{champs["championName"]}</h3>
							</li>
						))}
				</div>
			</div>
			<div className={styles.rightSide}>
				<h2>Most played champs</h2>
				<div className={styles.mostPlayedChamps}>
					{data.top_mastery
						.filter((champs: ChampionMastery) => champs.championName !== "Unknown")
						.map((champs: ChampionMastery) => (
							<li key={champs["championId"]}>
								<Image
									src={
										"http://localhost:8000/static/champion/" +
										champs["championIdString"] +
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
				<h2>Matchs history</h2>
				<MatchsHistory puuid={data.summoner.puuid} />
			</div>
		</div>
	);
}
