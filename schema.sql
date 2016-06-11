DROP TABLE IF EXISTS pastes, dailystats, stats;
\connect postgres
DROP DATABASE IF EXISTS pastebin;
CREATE ROLE pastebin WITH LOGIN PASSWORD '1234';
CREATE DATABASE pastebin OWNER pastebin;
GRANT ALL PRIVILEGES ON DATABASE pastebin TO pastebin;
\connect pastebin
CREATE TABLE pastes(
	pasteid 	varchar(32) PRIMARY KEY NOT NULL,
	token 		varchar(32)		NOT NULL,
	lexer 		varchar(512) 		NOT NULL,
	expiration 	timestamp 		NOT NULL,
	burn 		int 			NOT NULL,
	paste 		text 			NOT NULL,
	size		int			,
	lines		int			,
	sloc		int
);
CREATE TABLE stats (
	metric	varchar(32) PRIMARY KEY NOT NULL,
	counter bigserial NOT NULL
);
CREATE TABLE dailystats (
	date  		timestamp PRIMARY KEY	NOT NULL,
	pastecount 	bigserial 		NOT NULL,
	pasteviews 	bigserial 		NOT NULL
);

INSERT INTO stats (metric, counter) VALUES ('totalpastes', 0);
INSERT INTO stats (metric, counter) VALUES ('totalviews', 0);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pastebin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pastebin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pastebin;

