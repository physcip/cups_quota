CREATE TABLE users(username varchar(255) primary key not null, pagequota unsigned int, lastjob datetime, pagecount unsigned int);
CREATE TABLE config(key varchar(255), value unsigned int);
INSERT INTO config (key, value) VALUES ( "lastupdate", strftime('%s', 'now') );
