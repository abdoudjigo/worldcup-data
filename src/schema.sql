-- Base de données : worldcup

-- 1. Tournois
CREATE TABLE tournois (
    id              SERIAL PRIMARY KEY,
    annee           INTEGER NOT NULL UNIQUE,
    pays_hote       VARCHAR(100) NOT NULL,
    ville_hote      VARCHAR(100),
    date_debut      DATE,
    date_fin        DATE,
    nb_equipes      INTEGER,
    nb_matchs       INTEGER,
    nb_stades       INTEGER
);

-- 2. Equipes
CREATE TABLE equipes (
    id              SERIAL PRIMARY KEY,
    nom             VARCHAR(100) NOT NULL UNIQUE,
    code_pays       CHAR(3)
);

-- 3. Stades
CREATE TABLE stades (
    id              SERIAL PRIMARY KEY,
    nom             VARCHAR(150) NOT NULL UNIQUE,
    ville           VARCHAR(100),
    pays            VARCHAR(100),
    capacite        INTEGER
);

-- 4. Matchs
CREATE TABLE matchs (
    id              SERIAL PRIMARY KEY,
    tournoi_id      INTEGER REFERENCES tournois(id),
    stade_id        INTEGER REFERENCES stades(id),
    equipe_dom_id   INTEGER REFERENCES equipes(id),
    equipe_ext_id   INTEGER REFERENCES equipes(id),
    score_dom       INTEGER,
    score_ext       INTEGER,
    score_mi_temps_dom  INTEGER,
    score_mi_temps_ext  INTEGER,
    date_match      DATE,
    heure           TIME,
    timezone        VARCHAR(10),
    phase           VARCHAR(50),  -- 'Groupe A', 'Semi-final', 'Final'...
    groupe          VARCHAR(10),  -- 'A', 'B', '1', '2'... NULL si phase finale
    prolongation    BOOLEAN DEFAULT FALSE,
    tirs_au_but     BOOLEAN DEFAULT FALSE
);

-- 5. Joueurs
CREATE TABLE joueurs (
    id              SERIAL PRIMARY KEY,
    nom             VARCHAR(100) NOT NULL,
    prenom          VARCHAR(100),
    date_naissance  DATE,
    poste           VARCHAR(5),   -- GK, DF, MF, FW
    equipe_id       INTEGER REFERENCES equipes(id)
);

-- 6. Compositions
CREATE TABLE compositions (
    id                      SERIAL PRIMARY KEY,
    match_id                INTEGER REFERENCES matchs(id),
    joueur_id               INTEGER REFERENCES joueurs(id),
    equipe_id               INTEGER REFERENCES equipes(id),
    est_capitaine           BOOLEAN DEFAULT FALSE,
    minute_remplacement     INTEGER  -- NULL si pas remplacé
);

-- 7. Buts
CREATE TABLE buts (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER REFERENCES matchs(id),
    joueur_id   INTEGER REFERENCES joueurs(id),
    equipe_id   INTEGER REFERENCES equipes(id),
    minute      INTEGER,
    type        VARCHAR(20) DEFAULT 'normal'
                CHECK (type IN ('normal', 'penalty', 'contre_son_camp'))
);

-- 8. Arbitres
CREATE TABLE arbitres (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    prenom      VARCHAR(100),
    nationalite CHAR(3)
);

-- 9. Table intermédiaire matchs <-> arbitres
CREATE TABLE matchs_arbitres (
    id          SERIAL PRIMARY KEY,
    match_id    INTEGER REFERENCES matchs(id),
    arbitre_id  INTEGER REFERENCES arbitres(id),
    role        VARCHAR(30) DEFAULT 'principal'
);