// components/BackgroundImage.tsx
"use client";
import { usePathname } from "next/navigation";
import styles from "./BackgroundImage.module.css";

export default function BackgroundImage() {
	const pathname = usePathname();
	if (pathname !== "/") return null;
	return (<div className={styles.backgroundImage}></div>);
}