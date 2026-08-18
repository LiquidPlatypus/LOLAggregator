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
		<div>
			<h1>
				{data.player.gameName}#{data.player.tagLine}
			</h1>
		</div>
	);
}
