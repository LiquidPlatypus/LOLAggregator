# LOLAggregator — Contexte du projet

## Objectif
Site perso pour rechercher un joueur League of Legends (via Riot API) et afficher ses stats (profil, champions joués, historique de matchs). Remplace une ancienne version en Streamlit.

## Mode de travail avec Claude
**Mode tuteur strict** : Claude ne donne jamais la solution directement. Il pose des questions/indices, laisse au moins 2 tentatives avant de donner la réponse complète (sauf demande explicite de "donne moi la réponse"). Réponses courtes, une notion à la fois, questions de vérification régulières.

## Architecture générale
- `backend/` : Python + FastAPI (logique métier, appels Riot API, transformation des données)
- `frontend/` : Next.js (App Router) + TypeScript + CSS Modules (pas de Tailwind — préférence explicite de l'utilisateur, jugé peu lisible)
- Communication : frontend fetch le backend en HTTP/JSON (`http://localhost:8000`)
- **Base de données : PostgreSQL, lancée via Docker (conteneur `lolaggregator-db`)** — mise en place cette session (voir section dédiée plus bas)
- Déploiement futur envisagé (pas encore fait) : Docker (1 conteneur par service : backend, frontend, nginx, DB), docker-compose pour orchestrer, Nginx en reverse proxy. **Ordre retenu : d'abord faire fonctionner chaque service en local, Docker vient ensuite encapsuler ce qui marche déjà — pas l'inverse.**

## Décisions clés du backend
- **Gestion d'erreurs Riot** : `_get()` dans `riot.py` utilise `response.raise_for_status()` pour détecter les erreurs HTTP (429, 401, 404...) au lieu de laisser un JSON d'erreur silencieux remonter jusqu'à `process_matches` (cause de `KeyError` confus). Chaque route (`read_player`, `read_match`) a un `try/except requests.exceptions.HTTPError` qui lève une `HTTPException` FastAPI avec le vrai status code Riot.
- **Retry automatique sur 429** : `_get()` boucle en `while True`, détecte `response.status_code == 429`, lit le header standard HTTP `Retry-After` (nombre de secondes à attendre, envoyé uniquement sur une réponse 429) et fait `time.sleep(retry_after)` avant de retenter. `raise_for_status()` et `return response.json()` doivent être **à l'intérieur** de la boucle `while` (bug vécu : mal indentés = boucle infinie silencieuse dès qu'un 429 survient, jamais de retour).
- **Rate limit Riot (clé dev)** : deux fenêtres à respecter simultanément, visibles dans les headers `X-App-Rate-Limit` (limites) et `X-App-Rate-Limit-Count` (consommation actuelle), format `requêtes:secondes` — ex. `100:120,20:1` = 100 req/120s ET 20 req/1s. La fenêtre la plus stricte (ici 20/1s) peut déclencher un 429 même très loin de la limite globale.
- **CORS** : `CORSMiddleware` ajouté dans `main.py` (origins autorisées : `localhost:3000`) — nécessaire car les fetchs depuis les Client Components (ex: `MatchsHistory.tsx`) partent du navigateur, contrairement aux Server Components qui fetchent côté serveur sans restriction CORS.
- **Pagination des matchs** : endpoint séparé `/matchs/{puuid}?page=X&count=Y` (retiré de `/player/...`). `start = (page - 1) * count` calculé côté backend. Parallélisation des appels `get_match` avec `ThreadPoolExecutor` (gain perf ~4s → quasi instantané pour 10 matchs).
- **`python3 -u`** obligatoire pour voir les `print()` en temps réel lors de scripts longs (scraper) — sinon stdout bufferisé, aucun affichage avant la fin (ou un blocage qui semble silencieux).

### Endpoints (volontairement limités à 2, groupés par besoin frontend, pas par ressource)
- `GET /player/{game_name}/{tag_line}` → renvoie player + summoner + mastery + top_mastery + matchs_history combinés
- `/matches/...` pas encore créé séparément — l'historique est actuellement inclus dans `/player/...`

### Structure des fichiers Python
- `main.py` : routes FastAPI, **orchestration uniquement** (appelle les fonctions, assemble le retour) — pas de logique métier dedans
- `api/riot.py` : appels bruts à l'API Riot (`get_player`, `get_summoner`, `get_champion_mastery`, `get_match_history`, `get_match`), retry 429 intégré dans `_get`
- `api/dragon.py` : lecture des données statiques Dragontail (`load_champions`, `load_items`)
- `data/processor.py` : toute la logique de transformation/tri (`process_mastery`, `get_top_champs`, `process_matches`)
- `config.py` : variables d'env (`API_KEY`, `REGION`, `PLATFORM`, `DRAGON_PATH`, `USE_LOCAL_DATA`)
- `scraper.py` : scraping one-shot de toutes les données perso (matchs + profil) vers des JSON locaux, relançable pour update (skip si déjà présent)
- `local_data.py` : lecture des JSON scrapés, avec la **même signature** que les fonctions `riot.py` équivalentes (permet l'alias transparent)
- `database/` : package Postgres (`connection.py`, `models.py`, `init_db.py`, `populate_static.py`) — voir section dédiée

### Points techniques importants côté backend
- **Fichiers statiques** : images Dragontail (profileicon, champion) servies via `StaticFiles` de FastAPI, montées sur `/static` → `http://localhost:8000/static/champion/{championIdString}.png` ou `/static/profileicon/{profileIconId}.png`
- **`load_champions()`** renvoie un dict `{championId (int): {"id": "NomNormalisé", "name": "Nom Affiché"}}` — nécessaire car les noms de fichiers Dragontail (`champion["id"]`) n'ont pas d'accents/apostrophes contrairement aux noms affichés (`champion["name"]`), ex: Kai'Sa, Séraphine
- **`load_items()`** (nouveau) : même pattern que `load_champions`, lit `item.json`. Filtre indispensable : `item.get("gold", {}).get("purchasable", False)` — sans ce filtre, des items spéciaux liés à des capacités de champion (ex: munitions de Gangplank, `requiredChampion` défini, `gold.purchasable: false`) polluent la liste avec des noms/descriptions au format HTML très long. Le champ `inStore` est **trompeur** : absent sur la plupart des vrais items, et toujours `false` quand présent — ne pas s'y fier.
- **Gestion des NaN** : `pd.json_normalize` sur des données Riot API crée des colonnes avec NaN quand une clé est absente pour certaines entrées (ex: milestones de mastery, challenges de match selon le rôle joué). Pattern retenu : cibler par type de colonne avec `df.select_dtypes(include="number")` → `fillna(0)`, et `select_dtypes(exclude="number")` → `fillna("")`. Ne jamais faire un `fillna` générique sur tout le DataFrame sans réfléchir (casse les colonnes contenant des listes).
- **Encoding** : toujours ouvrir les fichiers Dragontail avec `encoding="utf-8"` pour éviter les problèmes d'accents mal interprétés
- **`process_matches(matches_raw, puuid)`** : pour chaque match, cherche le participant correspondant au puuid recherché via `next((p for p in match["info"]["participants"] if p["puuid"] == puuid), None)`, puis construit une liste de `{"match": match, "participant": participant}` avant le `json_normalize`. Résultat : après normalize, les clés sont préfixées `match.info.gameId`, `participant.championName`, `participant.kills`, etc.
- **Dragontail version** : dossier `dragontail-16.16.1/16.16.1/data/fr_FR/`, chemin construit via `os.path.join(DRAGON_PATH, "champion.json")`. Penser à mettre à jour la version régulièrement (nouveaux champions sinon `championName` = "Unknown").
- **`.env`** nécessite un redémarrage serveur pour être rechargé après modif.

## Scraper local (pont temporaire dev, avant la DB)
**Objectif** : éviter de rappeler l'API Riot en boucle pendant le dev (limite dev key = 100 req/2min + 20 req/1s), en aspirant une fois toutes les données perso et en les rejouant depuis le disque.

- **`scraper.py`** :
  - `get_all_match_ids(puuid, count=100)` : pagine tout l'historique via `start`/`count`, s'arrête dès qu'une page renvoie moins de `count` résultats (edge case connu et accepté : si le total est un multiple exact de `count`, la détection de fin échoue — pas grave pour un usage perso)
  - `scrape_matches(puuid, match_ids)` : sauvegarde chaque match dans `data/scraped/matches/{match_id}.json` (chemin **plat**, sans sous-dossier par `puuid` — un match_id est unique en soi, pas besoin de le ranger par joueur). Skip via `os.path.exists` si le fichier existe déjà → relançable à volonté pour ne récupérer que les nouveaux matchs
  - `scrape_profile(puuid)` : sauvegarde `summoner.json` et `mastery.json` dans `data/scraped/{puuid}/`
  - `main()` : `puuid` hardcodé pour l'instant, enchaîne `scrape_profile` puis `get_all_match_ids` + `scrape_matches`
  - Se lance avec `python3 -u scraper.py` (le `-u` est important, voir plus haut)

- **`local_data.py`** : miroir en lecture de `scraper.py`, avec `load_json(filepath)` factorisée (un seul point de lecture/erreur, réutilisé par toutes les fonctions) :
  - `load_local_match(match_id)`, `load_local_summoner(puuid)`, `load_local_mastery(puuid)`
  - `load_local_match_ids(puuid=None, start=0, count=100)` : liste les fichiers dans `data/scraped/matches/`, **trie par ID décroissant** (`match_ids.sort(key=lambda mid: int(mid.split("_")[1]), reverse=True)` — la partie numérique de l'ID Riot est croissante avec le temps, donc suffisant pour trier chronologiquement sans ouvrir chaque JSON), puis slice `[start:start+count]` pour reproduire une vraie pagination. `puuid` gardé en paramètre mais ignoré (juste pour matcher la signature de `get_match_history`)

- **Bascule dev/prod (`USE_LOCAL_DATA`)** : flag dans `.env`/`config.py`. Dans `main.py`, import conditionnel avec alias (`load_local_summoner as get_summoner`, etc.) — `read_player` et le reste du code n'ont **aucune idée** de la source réelle des données, transparence totale grâce aux alias + signatures identiques entre `riot.py` et `local_data.py`.

- **Bug vécu (résolu)** : `os.listdir` ne garantit pas d'ordre stable → sans le tri, pagination incohérente d'un appel à l'autre.

## Base de données PostgreSQL (mise en place cette session)

### Setup
- Conteneur Docker : `docker run --name lolaggregator-db -e POSTGRES_PASSWORD=... -e POSTGRES_DB=lolaggregator -p 5432:5432 -d postgres`
- Connexion via `CONNECTION_STRING` dans `.env` backend, format `postgresql://postgres:MOTDEPASSE@localhost:5432/lolaggregator`
- Client d'exploration utilisé : DataGrip (même identifiants que la connection string)
- **Venv backend nettoyé** cette session : l'ancien venv traînait tous les résidus de la version Streamlit (`streamlit`, `altair`, `plotly`, `jupyter`...). Nouveau venv créé, dépendances réinstallées proprement : `fastapi`, `uvicorn`, `requests`, `pandas`, `python-dotenv`, `sqlalchemy`, `psycopg2-binary`. `requirements.txt` regénéré via `pip freeze`.

### Structure du package `database/`
- **`database/connection.py`** : `engine` (via `create_engine(CONNECTION_STRING)`), `Base` (via `class Base(DeclarativeBase)`), `Session` (fabrique via `sessionmaker(engine)`)
- **`database/models.py`** : toutes les classes de tables (choix : un seul fichier plutôt qu'un fichier par table, pour éviter les imports circulaires vu le nombre de relations croisées entre les 8 tables). Import relatif `from .connection import Base`.
- **`database/__init__.py`** : fichier vide, nécessaire pour que Python reconnaisse `database/` comme un vrai package et accepte les imports relatifs (`from .connection import ...`) — sans lui, PyCharm/Python lève une erreur "relative import outside of a package".
- **`database/init_db.py`** : script one-shot, importe toutes les classes de `models.py` (nécessaire pour que `Base.metadata` les "voie") puis `Base.metadata.create_all(engine)`. Lancé une fois avec `python -m database.init_db`.
- **`database/populate_static.py`** : peuple `Champion` et `Item` depuis Dragontail. Ouvre une seule `Session()`, boucle sur `load_champions()`/`load_items()`, `session.get(Champion, id)` (recherche par clé primaire) pour skip si déjà présent avant chaque `session.add(...)`, un seul `commit()`/`close()` à la fin (hors des boucles). Lancé avec `python -m database.populate_static`, relançable sans erreur de doublon.

### Schéma (8 tables)

**Tables statiques** (peuplées depuis Dragontail, pas depuis l'API Riot) :
- **`Champion`** : `id` (PK), `name` (nom affiché), `normalized_name` (nom fichier, sans accents)
- **`Item`** : `id` (PK), `name` (`String(100)`), `description`/`plaintext` (**`Text`**, pas `String` — les descriptions HTML de certains items dépassent largement 500 caractères), `gold` (`Integer`, extrait de `gold.total` dans le JSON brut — `gold` est un objet avec base/total/sell/purchasable, pas juste un nombre), `tags` (`Mapped[list[str]]` + `mapped_column(JSON)`), `stats` (`Mapped[dict[str, Any]]` + `mapped_column(JSON)`, `Any` importé de `typing`). **Filtre à l'insertion** : seuls les items avec `gold.purchasable == True` sont gardés (voir section backend plus haut).

**Tables dynamiques** (à peupler depuis le scraper/API — prochaine étape) :
- **`User`** : `id` (PK technique), `puuid` (`unique=True`), `game_name`, `tag_line` (`String(10)`, marge de sécurité au-delà des ~5 caractères habituels)
- **`Summoner`** : `id` (PK), `user_id` (FK → `User.id`), `profile_icon_id`, `summoner_level` — séparée de `User` car ces données évoluent dans le temps
- **`Match`** : `id` (PK technique), `game_id` (`unique=True`), `match_id` (`String(50)`, `unique=True`), `game_duration`, `game_creation` — table indépendante des joueurs (rien ici ne dépend d'un `user` précis)
- **`Participation`** : table de jointure `User` ↔ `Match` (many-to-many : un match a 10 joueurs, un joueur a plusieurs matchs). `user_id` (FK), `match_id` (FK), + tout ce qui dépend de la **combinaison** joueur+match : `champion_name`, `kills`, `deaths`, `assists`, `win` (`Mapped[bool]`, pas besoin de préciser le type SQL, déduit automatiquement)
- **`ChampionMastery`** : table de jointure `User` ↔ `Champion`. `user_id` (FK), `champion_id` (FK), `champion_points`, `champion_level`
- **`Participation_item`** : table de jointure `Participation` ↔ `Item` (un joueur a plusieurs items dans un match, un item apparaît dans plusieurs participations). `participation_id` (FK), `item_id` (FK) — pas de colonne supplémentaire, sert uniquement de lien. Représente l'**inventaire final** (`item0`-`item6` déjà présents dans les données participant Riot), pas l'historique d'achat complet (nécessiterait l'API timeline, mise de côté — voir plus bas).

**Principe retenu à chaque table** : une info vit à l'endroit qui a la bonne "granularité" — au niveau `Match` si elle concerne le match entier (`gameDuration`), au niveau `Participation` si elle dépend du joueur+match (`championName`, `kills`). Dès qu'une relation est "plusieurs à plusieurs", passer par une table de jointure plutôt qu'une FK directe.

### Concepts SQLAlchemy vus cette session (pour quelqu'un venant de Prisma)
- Une table = une classe Python héritant de `Base`, avec `__tablename__` et des attributs `Mapped[type_python] = mapped_column(TypeSQL, options...)`
- `Mapped[...]` attend un type **Python** (`int`, `str`, `bool`, `list[str]`, `dict[str, Any]`), pas un type SQL — les deux sont donnés séparément (annotation + `mapped_column(...)`)
- FK simple : `mapped_column(ForeignKey("NomTable.colonne"))` (string, pas une référence directe à la classe)
- Une session s'obtient via la fabrique : `session = Session()`, puis `session.add(obj)` (répété autant de fois que nécessaire), et un seul `session.commit()` + `session.close()` à la fin — pas par itération de boucle
- `session.get(Classe, cle_primaire)` : recherche rapide par PK, renvoie l'objet ou `None`
- Erreur classique : oublier d'importer les classes de `models.py` avant `Base.metadata.create_all(engine)` → la table n'est pas créée car `Base` ne "voit" que ce qui a été importé

## Décisions clés du frontend
- **Recherche joueur avec vérification silencieuse** : `SearchBar.tsx` fait un debounce de 500ms (`setTimeout` + `clearTimeout` en cleanup de `useEffect`) sur `[gameName, tagLine]`. Si les deux champs sont non-vides après le délai, fetch `/player/{gameName}/{tagLine}` ; si `200`, affiche une carte cliquable sous la barre (photo + gameName#tagLine) via un state `foundPlayer: PlayerResponse | null` ; sinon carte masquée. Clic sur la carte → redirige vers `/profile?...`. Pas de bouton "Search" nécessaire. Riot n'offre pas de recherche par préfixe/autocomplétion (seulement gameName+tagLine exacts) — contrainte API, pas de contournement simple sans base de données perso.
- **MatchsHistory (pagination lazy)** : composant Client (`"use client"`) qui reçoit seulement `puuid` en prop (pas les matchs directement). `useEffect` sur `[puuid, pageNumber]` fetch `/matchs/{puuid}?page=...`. States : `pageNumber`, `matchsList`, `isLastPage` (détecté si la réponse a moins de `count` matchs — pas fiable si le total est un multiple exact de `count`, edge case connu non résolu), `errorMessage`, `isLoading`. Input numérique pour sauter directement à une page (pratique pour tester/débugger sans cliquer en boucle). Clic sur un match → redirige vers `/match?id=...`.
- **Types centralisés dans `page.tsx`** : `Player`, `Summoner`, `PlayerResponse`, `ChampionMastery`, `Matchs` sont actuellement définis dans `src/app/profile/page.tsx` et importés depuis les autres composants (`MatchsHistory.tsx`, `SearchBar.tsx`). Ce n'est pas l'endroit idéal (page vs fichier de types dédié) — amélioration à faire : déplacer vers un fichier `types.ts` séparé.

### Structure
- `src/app/page.tsx` : page d'accueil (Server Component)
- `src/app/profile/page.tsx` : page profil (Server Component `async`, fetch direct le backend)
- `src/app/layout.tsx` : layout racine avec `<Header />` et `<Footer />` dans `<body>`, autour de `{children}`
- `src/components/SearchBar.tsx` : Client Component (`"use client"`), isolé pour ne pas rendre tout le Header/layout "client"
- `src/components/Header.tsx`, `Footer.tsx` : Server Components qui importent SearchBar (un Server Component peut afficher un Client Component sans problème, l'inverse n'est pas vrai sans précaution)
- `src/components/MatchsHistory.tsx` : Client Component, pagination + navigation vers `/match?id=...` au clic sur un match

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
  - **Style visuel searchbar** : effet "glassmorphism" (clear glass) — `background-color: rgba(255,255,255,0.2)` + `backdrop-filter: blur(20px)` + bordure fine. Le flou nécessite un élément séparé en `position: fixed` (couvrant toute la fenêtre, avec les mêmes propriétés flex que `.page` pour garder le centrage) plutôt que directement sur l'élément qui porte l'image de fond — sinon un élément ne peut pas se flouter "lui-même".

## Fonctionnalités discutées mais pas encore implémentées
- Affichage détaillé d'un match au clic (nécessite garder toutes les données de match — décision prise de tout renvoyer depuis le backend plutôt que de faire un endpoint détail séparé, cf. Option A retenue). Route `/match?id=...` déjà présente côté frontend (clic depuis `MatchsHistory.tsx`), page pas encore construite.
- `error.tsx` (filet de sécurité pour erreurs non prévues, backend injoignable)
- Sélecteur de langue (visible dans le wireframe header, jamais implémenté)
- Compteur "nombre de games jouées par champion" — pas disponible via l'API mastery, nécessiterait de compter depuis l'historique de matchs
- **Fiche détaillée par champion (stats agrégées)** : nouvel endpoint `/champion-stats/{puuid}?count=100` — fetch les N derniers matchs, groupe par `participant.championName` avec `pandas.groupby()`, calcule pour chaque champion : nombre de games, winrate, KDA moyen. Décision : calculer TOUS les champions d'un coup plutôt qu'un par un. **Doit maintenant s'appuyer sur la DB** (requêtes SQL) plutôt que sur des refetchs API — voir raisonnement ci-dessous.
- **Stats par item (optionnellement filtrées par champion)** : ex. "winrate quand j'ai Infinity Edge sur Jinx". Requête = jointure `Participation_item` (filtre `item_id`) + `Participation` (filtre `championName`, lit `win`) → agrégation. La table statique `Item` ne sert que pour l'affichage (nom, image), pas pour le calcul.
- **Pourquoi la DB est indispensable (pas juste un confort dev)** : même avec une clé API de prod (limite plus haute), refetcher l'historique complet d'un joueur à chaque visite de page reste un problème — (1) ça ne scale pas avec le nombre de visiteurs/visites répétées, (2) un match une fois joué ne change **jamais**, donc le refetch est un gaspillage même sans contrainte de rate limit. La DB cache les matchs une fois pour toutes ; filtrer par champion/item devient une requête SQL plutôt qu'un fetch API.
- **Timeline horizontale des achats d'items** croisée aux events du match (kills/objectifs) et au matchup adverse (même rôle/lane, via `teamPosition`) — nécessite l'API timeline Riot (`/lol/match/v5/matches/{matchId}/timeline`, call séparé et coûteux), une table DB dédiée aux events avec timestamps. Explicitement mise de côté : trop ambitieuse avant d'avoir la DB de base fonctionnelle. Présentation envisagée : axe temporel horizontal avec icônes d'items placées au moment de l'achat + marqueurs d'events au-dessus.

## Bugs résolus (pour référence, éviter de refaire les mêmes erreurs)
- NaN dans mastery → `.fillna()` ciblé par colonne
- Version Dragontail périmée → champion manquant (`championName` = "Unknown" en fallback)
- Erreur d'hydratation React causée par l'extension navigateur Dark Reader (pas un bug de code — vérifier en navigation privée en cas de doute)
- `next/image` bloque `localhost` par défaut (SSRF protection) → `remotePatterns` + `dangerouslyAllowLocalIP`
- Boucle infinie silencieuse dans `_get` (retry 429) : `raise_for_status()`/`return` mal indentés, hors de la `while` → jamais de sortie de boucle en cas de succès
- `os.listdir` sans tri → pagination locale incohérente (ordre non garanti par le filesystem)
- Signature incompatible entre `get_match(match_id)` (API, 1 argument) et `load_local_match(puuid, match_id)` (2 arguments) → réglé en simplifiant le stockage des matchs en chemin plat (`data/scraped/matches/`), plus besoin du `puuid` pour retrouver un match
- `String(500)` trop court pour les descriptions d'items Riot (HTML) → passé en `Text` (longueur illimitée)
- Champ `inStore` de Dragontail trompeur pour filtrer les items achetables (absent sur la plupart des vrais items, toujours `false` quand présent) → utiliser `gold.purchasable == True` à la place
- `UniqueViolation` en relançant un script de population → ajout d'un check `session.get(Classe, id)` avant chaque `session.add()` pour skip les entrées déjà présentes, plutôt que de vider/recréer la table à chaque run

## Prochaine étape immédiate
Peupler les tables **dynamiques** (`User`, `Summoner`, `Match`, `Participation`, `ChampionMastery`, `Participation_item`) depuis les JSON déjà scrapés (`data/scraped/`) — plus complexe que `populate_static.py` car il faut résoudre les relations entre tables (retrouver/créer le `User` avant d'insérer sa `Participation`, etc.) au lieu d'inserts indépendants.