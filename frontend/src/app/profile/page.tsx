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

interface Matchs {
	"match.info.gameId": number;
	"match.metadata.matchId": string;
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
	const data = await res.json();

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
				<div className={styles.champsList}>
					{data.mastery.filter(champs => (champs.championName !== "Unknown")).map((champs: ChampionMastery) => (
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
				<div className={styles.mostPlayedChamps}>
					{data.top_mastery.filter(champs => (champs.championName !== "Unknown")).map((champs: ChampionMastery) => (
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
				<div className={styles.matchsHistory}>
					{data.matchs_history.map((match: Matchs) => (
						<li key={match["match.info.gameId"]}>
							<p>{match["match.metadata.matchId"]}</p>
						</li>
					))}
				</div>
			</div>
		</div>
	);
}
