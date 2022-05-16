

CREATE KEYSPACE IF NOT EXISTS news 
WITH REPLICATION = 
{'class':'SimpleStrategy', 'replication_factor':'1'};

CREATE TABLE IF NOT EXISTS news.news_table (
uuiid UUID,
author TEXT,
title TEXT,
description TEXT,
url TEXT, 
source TEXT, 
image TEXT,
category TEXT,
language TEXT,
country TEXT,
published_at TEXT, 
PRIMARY KEY((uuiid), source));