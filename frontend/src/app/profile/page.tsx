export default async function profilePage({ searchParams }) {
	const { gameName, tagLine } = await searchParams;
	const res = await fetch(`http://localhost:8000/player/${gameName}/${tagLine}`);
	const data = await res.json();

	return (
		<div>
			<h1>
				{data.player.gameName}#{data.player.tagLine}
			</h1>
		</div>
	);
}
