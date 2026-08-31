# LOLAggregator — Contexte du projet

## Objectif
Site perso pour rechercher un joueur League of Legends (via Riot API) et afficher ses stats (profil, champions joués, historique de matchs). Remplace une ancienne version en Streamlit.

## Mode de travail avec Claude
**Mode tuteur strict** : Claude ne donne jamais la solution directement. Il pose des questions/indices, laisse au moins 2 tentatives avant de donner la réponse complète (sauf demande explicite de "donne moi la réponse"). Réponses courtes, une notion à la fois, questions de vérification régulières.

## Architecture générale
- `backend/` : Python + FastAPI (logique métier, appels Riot API, transformation des données)
- `frontend/` : Next.js (App Router) + TypeScript + CSS Modules (pas de Tailwind — préférence explicite de l'utilisateur, jugé peu lisible)
- Communication : frontend fetch le backend en HTTP/JSON (`http://localhost:8000`)
- Déploiement futur envisagé (pas encore fait) : Docker (1 conteneur par service : backend, frontend, nginx, DB), docker-compose pour orchestrer, Nginx en reverse proxy, DB pour cacher les matchs et limiter les appels API (limite Riot : 20 calls/s)

## Décisions clés du backend
- **Gestion d'erreurs Riot** : `_get()` dans `riot.py` utilise `response.raise_for_status()` pour détecter les erreurs HTTP (429, 401, 404...) au lieu de laisser un JSON d'erreur silencieux remonter jusqu'à `process_matches` (cause de `KeyError` confus). Chaque route (`read_player`, `read_match`) a un `try/except requests.exceptions.HTTPError` qui lève une `HTTPException` FastAPI avec le vrai status code Riot.
- **CORS** : `CORSMiddleware` ajouté dans `main.py` (origins autorisées : `localhost:3000`) — nécessaire car les fetchs depuis les Client Components (ex: `MatchsHistory.tsx`) partent du navigateur, contrairement aux Server Components qui fetchent côté serveur sans restriction CORS.
- **Pagination des matchs** : endpoint séparé `/matchs/{puuid}?page=X&count=Y` (retiré de `/player/...`). `start = (page - 1) * count` calculé côté backend. Parallélisation des appels `get_match` avec `ThreadPoolExecutor` (gain perf ~4s → quasi instantané pour 10 matchs).

### Endpoints (volontairement limités à 2, groupés par besoin frontend, pas par ressource)
- `GET /player/{game_name}/{tag_line}` → renvoie player + summoner + mastery + top_mastery + matchs_history combinés
- `/matches/...` pas encore créé séparément — l'historique est actuellement inclus dans `/player/...`

### Structure des fichiers Python
- `main.py` : routes FastAPI, **orchestration uniquement** (appelle les fonctions, assemble le retour) — pas de logique métier dedans
- `api/riot.py` : appels bruts à l'API Riot (`get_player`, `get_summoner`, `get_champion_mastery`, `get_match_history`, `get_match`)
- `api/dragon.py` : lecture des données statiques Dragontail (`load_champions`)
- `data/processor.py` : toute la logique de transformation/tri (`process_mastery`, `get_top_champs`, `process_matches`)
- `config.py` : variables d'env (`API_KEY`, `REGION`, `PLATFORM`, `DRAGON_PATH`)

### Points techniques importants côté backend
- **Fichiers statiques** : images Dragontail (profileicon, champion) servies via `StaticFiles` de FastAPI, montées sur `/static` → `http://localhost:8000/static/champion/{championIdString}.png` ou `/static/profileicon/{profileIconId}.png`
- **`load_champions()`** renvoie un dict `{championId (int): {"id": "NomNormalisé", "name": "Nom Affiché"}}` — nécessaire car les noms de fichiers Dragontail (`champion["id"]`) n'ont pas d'accents/apostrophes contrairement aux noms affichés (`champion["name"]`), ex: Kai'Sa, Séraphine
- **Gestion des NaN** : `pd.json_normalize` sur des données Riot API crée des colonnes avec NaN quand une clé est absente pour certaines entrées (ex: milestones de mastery, challenges de match selon le rôle joué). Pattern retenu : cibler par type de colonne avec `df.select_dtypes(include="number")` → `fillna(0)`, et `select_dtypes(exclude="number")` → `fillna("")`. Ne jamais faire un `fillna` générique sur tout le DataFrame sans réfléchir (casse les colonnes contenant des listes).
- **Encoding** : toujours ouvrir les fichiers Dragontail avec `encoding="utf-8"` pour éviter les problèmes d'accents mal interprétés
- **`process_matches(matches_raw, puuid)`** : pour chaque match, cherche le participant correspondant au puuid recherché via `next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)`, puis construit une liste de `{"match": match, "participant": participant}` avant le `json_normalize`. Résultat : après normalize, les clés sont préfixées `match.info.gameId`, `participant.championName`, `participant.kills`, etc.
- **Dragontail version** : dossier `dragontail-16.16.1/16.16.1/data/fr_FR/`, chemin construit via `os.path.join(DRAGON_PATH, "champion.json")`. Penser à mettre à jour la version régulièrement (nouveaux champions sinon `championName` = "Unknown").
- **`.env`** nécessite un redémarrage serveur pour être rechargé après modif.

## Décisions clés du frontend
- **Recherche joueur avec vérification silencieuse** : `SearchBar.tsx` fait un debounce de 500ms (`setTimeout` + `clearTimeout` en cleanup de `useEffect`) sur `[gameName, tagLine]`. Si les deux champs sont non-vides après le délai, fetch `/player/{gameName}/{tagLine}` ; si `200`, affiche une carte cliquable sous la barre (photo + gameName#tagLine) via un state `foundPlayer: PlayerResponse | null` ; sinon carte masquée. Clic sur la carte → redirige vers `/profile?...`. Pas de bouton "Search" nécessaire. Riot n'offre pas de recherche par préfixe/autocomplétion (seulement gameName+tagLine exacts) — contrainte API, pas de contournement simple sans base de données perso.
- **MatchsHistory (pagination lazy)** : composant Client (`"use client"`) qui reçoit seulement `puuid` en prop (pas les matchs directement). `useEffect` sur `[puuid, pageNumber]` fetch `/matchs/{puuid}?page=...`. States : `pageNumber`, `matchsList`, `isLastPage` (détecté si la réponse a moins de `count` matchs — pas fiable si le total est un multiple exact de `count`, edge case connu non résolu), `errorMessage`, `isLoading`. Input numérique pour sauter directement à une page (pratique pour tester/débugger sans cliquer en boucle).
- **Types centralisés dans `page.tsx`** : `Player`, `Summoner`, `PlayerResponse`, `ChampionMastery`, `Matchs` sont actuellement définis dans `src/app/profile/page.tsx` et importés depuis les autres composants (`MatchsHistory.tsx`, `SearchBar.tsx`). Ce n'est pas l'endroit idéal (page vs fichier de types dédié) — amélioration à faire : déplacer vers un fichier `types.ts` séparé.

### Structure
- `src/app/page.tsx` : page d'accueil (Server Component)
- `src/app/profile/page.tsx` : page profil (Server Component `async`, fetch direct le backend)
- `src/app/layout.tsx` : layout racine avec `<Header />` et `<Footer />` dans `<body>`, autour de `{children}`
- `src/components/SearchBar.tsx` : Client Component (`"use client"`), isolé pour ne pas rendre tout le Header/layout "client"
- `src/components/Header.tsx`, `Footer.tsx` : Server Components qui importent SearchBar (un Server Component peut afficher un Client Component sans problème, l'inverse n'est pas vrai sans précaution)

### Concepts Server vs Client Component (Next.js App Router)
- Server Component par défaut : peut faire `fetch` directement dans le corps de la fonction (`async function Page()`), pas de state/hooks/event handlers
- Client Component (`"use client"` en toute première ligne, avant les imports) : nécessaire dès qu'il y a `useState`, `useEffect`, `onClick`, etc.

### Recherche joueur
- `SearchBar` : 2 inputs contrôlés (gameName, tagLine) + `useState`, submit via `onSubmit` sur le `<form>` (Entrée + bouton fonctionnent tous les deux nativement)
- Redirection via `useRouter().push()` de `next/navigation` (pas `<Link>` car navigation programmatique déclenchée par une action, pas un lien statique)
- URL cible : `/profile?gameName=...&tagLine=...`

### Page Profile
- Récupère `searchParams` (typé `Promise<{ gameName: string; tagLine: string }>`) avec `await`
- Fetch le backend, vérifie `res.ok` avant de continuer (pattern recommandé par la doc Next.js pour les erreurs "attendues" — pas de try/catch, juste `if (!res.ok) return <JSX />`)
- `error.tsx` (Client Component obligatoire, reçoit `error` + `retry`) réservé aux erreurs non prévues (crash réseau, etc.) — pas encore implémenté, juste discuté

### Images
- `next/image` (`<Image>`) utilisé pour toutes les images Dragontail
- Nécessite config dans `next.config.ts` : `images.remotePatterns` pour autoriser `localhost:8000/static/**`, et `images.dangerouslyAllowLocalIP = true` (sinon Next.js bloque les IP locales par sécurité SSRF)
- Utiliser `championIdString` (pas `championName`) pour construire les URLs d'images de champions (accents/apostrophes cassent les noms de fichiers)
- `priority={true}` sur les images visibles immédiatement (LCP) pour éviter le lazy-loading par défaut

### Types TypeScript définis
```ts
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
    "info.gameId": number;      // note: sera à corriger en "match.info.gameId" suite à la restructuration process_matches
    "metadata.matchId": string; // idem: "match.metadata.matchId"
}
```
⚠️ Ces interfaces datent d'avant le dernier changement de structure de `process_matches` — les clés doivent être mises à jour avec le préfixe `match.` (ex: `"match.info.gameId"`) et il faudra ajouter les champs `participant.*` utilisés (championName, kills, deaths, assists, win, etc.)

### CSS Modules
- Convention : `NomDuComposant.module.css` à côté du composant (`page.tsx` → `page.module.css`)
- Import : `import styles from "./X.module.css";` puis `className={styles.nomClasse}`
- Sélecteurs CSS Modules doivent être des classes/ids (pas de sélecteur de balise brut type `header { }` → erreur "Selector is not pure")
- Config Prettier retenue : tabs (pas d'espaces), pas de semicolons forcés sur les directives comme `"use client"` (attention aux parenthèses auto-ajoutées par certains configs, doit être `"use client";` sans parenthèses)

## Wireframes (Figma, décrits par l'utilisateur)
- **Page d'accueil** : titre "LOLAggregator" centré, barre de recherche en dessous, footer
- **Header (toutes pages)** : titre + searchbar alignés à gauche (dans un même groupe flex), sélecteur de langue à droite (`justify-content: space-between`)
- **Page Profile**, layout 2 colonnes (flex, 3 niveaux imbriqués) :
  - Colonne gauche : card profil (image + gamename#tagline + account level) en haut, liste complète des champions joués en dessous (flex column, empilés verticalement, prévu un bouton "load more" plus tard)
  - Colonne droite : "most played champs" (5 champions en grid `repeat(5, 1fr)`) en haut, tableau historique des matchs en dessous (grid `30px 1fr` pour colonnes icône/résumé)
  - - **Style visuel searchbar** : effet "glassmorphism" (clear glass) — `background-color: rgba(255,255,255,0.2)` + `backdrop-filter: blur(20px)` + bordure fine. Le flou nécessite un élément séparé en `position: fixed` (couvrant toute la fenêtre, avec les mêmes propriétés flex que `.page` pour garder le centrage) plutôt que directement sur l'élément qui porte l'image de fond — sinon un élément ne peut pas se flouter "lui-même".

## Fonctionnalités discutées mais pas encore implémentées
- Affichage détaillé d'un match au clic (nécessite garder toutes les données de match — décision prise de tout renvoyer depuis le backend plutôt que de faire un endpoint détail séparé, cf. Option A retenue)
- error.tsx (filet de sécurité pour erreurs non prévues, backend injoignable)
- Sélecteur de langue (visible dans le wireframe header, jamais implémenté)
- Compteur "nombre de games jouées par champion" — pas disponible via l'API mastery, nécessiterait de compter depuis l'historique de matchs
- - **Fiche détaillée par champion (stats agrégées)** : nouvel endpoint `/champion-stats/{puuid}?count=100` — fetch les N derniers matchs (100 pour commencer, en démo), groupe par `participant.championName` avec `pandas.groupby()`, calcule pour chaque champion : nombre de games, winrate (moyenne de `participant.win`), KDA moyen. Décision : calculer TOUS les champions d'un coup plutôt qu'un par un (le coût réseau des N fetchs est le même dans les deux cas, autant avoir une vue d'ensemble). Limite connue : sur l'historique complet (~600+ matchs), la limite Riot de 100 requêtes/2min rendrait le chargement trop long (~10-12min) — solution à terme : cache/DB pour stocker les stats déjà calculées plutôt que tout refetch à chaque visite (rejoint l'idée de DB déjà notée dans l'architecture générale).

## Bugs résolus (pour référence, éviter de refaire les mêmes erreurs)
- NaN dans mastery → `.fillna()` ciblé par colonne
- Version Dragontail périmée → champion manquant (`championName` = "Unknown" en fallback)
- Erreur d'hydratation React causée par l'extension navigateur Dark Reader (pas un bug de code — vérifier en navigation privée en cas de doute)
- `next/image` bloque `localhost` par défaut (SSRF protection) → `remotePatterns` + `dangerouslyAllowLocalIP`
