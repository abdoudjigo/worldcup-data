library(DBI)
library(RPostgres)
library(jsonlite)

# Connexion PostgreSQL
con <- dbConnect(
  RPostgres::Postgres(),
  dbname   = "worldcup",
  host     = "localhost",
  port     = 5432,
  user     = "postgres",
  password = "5853500"
)
library(bit64)