"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Searchbar() {
	const [gameName, setGameName] = useState("");
	const [tagLine, setTagLine] = useState("");

	const router = useRouter();

	return (
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
			/>
			<input
				type="text"
				placeholder="Tagline"
				value={tagLine}
				onChange={e => setTagLine(e.target.value)}
			/>
			<button type="submit">Search</button> {/* TODO: remplacer 'Search' by csv */}
		</form>
	);
}
