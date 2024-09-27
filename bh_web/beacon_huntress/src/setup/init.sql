/* To run script use command below
mysql beacon < init.sql
*/

/*********************************************************************
**  DATABASE
*********************************************************************/

CREATE DATABASE IF NOT EXISTS beacon;

/*********************************************************************
**  TABLES
*********************************************************************/

CREATE TABLE IF NOT EXISTS `beacon`.`beacon_group` (
  `group_id` int NOT NULL AUTO_INCREMENT,
  `uid` varchar(256) DEFAULT NULL,
  `dt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`group_id`)
);

CREATE TABLE IF NOT EXISTS `beacon`.`beacon` (
  `uid` varchar(256) DEFAULT NULL,
  `orig_bytes` float DEFAULT NULL,
  `source_ip` varchar(256) DEFAULT NULL,
  `source_port` int DEFAULT NULL,
  `port` int DEFAULT NULL,
  `dest_ip` varchar(256) DEFAULT NULL,
  `local_resp` int DEFAULT NULL,
  `missed_bytes` bigint DEFAULT NULL,
  `orig_pkts` bigint DEFAULT NULL,
  `orig_ip_bytes` bigint DEFAULT NULL,
  `community_id` varchar(256) DEFAULT NULL,
  `ts` float DEFAULT NULL,
  `proto` varchar(256) DEFAULT NULL,
  `duration` float DEFAULT NULL,
  `resp_ip_bytes` bigint DEFAULT NULL,
  `local_orig` int DEFAULT NULL,
  `service` varchar(256) DEFAULT NULL,
  `resp_pkts` bigint DEFAULT NULL,
  `history` varchar(256) DEFAULT NULL,
  `resp_bytes` float DEFAULT NULL,
  `resp_p` int DEFAULT NULL,
  `conn_state` varchar(256) DEFAULT NULL,
  `s_dns` text,
  `d_dns` text,
  `source_file` varchar(256) DEFAULT NULL,
  `src_row_id` int DEFAULT NULL,
  `delta_mins` float DEFAULT NULL,
  `delta_ms` float DEFAULT NULL,
  `dt` datetime DEFAULT NULL,
  `group_id` int DEFAULT NULL,
  `likelihood` decimal(6,2),
  KEY `group_id` (`group_id`),
  CONSTRAINT `beacon_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `beacon_group` (`group_id`)
);

CREATE TABLE IF NOT EXISTS `beacon`.`beacon_filter` (
  `ip` varchar(256) DEFAULT NULL,
  `short_desc` varchar(1000) DEFAULT NULL,
  `is_user` boolean DEFAULT TRUE,
  `dt` datetime DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS `beacon`.`beacon_log` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `group_id` int DEFAULT NULL,
  `log_file` varchar(256) DEFAULT NULL,
  `dt` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`),
  KEY `fk_beaconlog_groupid` (`group_id`),
  CONSTRAINT `fk_beaconlog_groupid` FOREIGN KEY (`group_id`) REFERENCES `beacon_group` (`group_id`)
);

CREATE TABLE IF NOT EXISTS `beacon`.`beacon_run_conf` (
  `uid` varchar(256) DEFAULT NULL,
  `config` text
);

CREATE TABLE IF NOT EXISTS  `beacon`.`conf_general` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `refresh_rate` int DEFAULT NULL,
  `raw_loc` varchar(256) DEFAULT NULL,
  `bronze_loc` varchar(256) DEFAULT NULL,
  `silver_loc` varchar(256) DEFAULT NULL,
  `gold_loc` varchar(256) DEFAULT NULL,
  `file_type` varchar(256) DEFAULT NULL,
  `overwrite` bit(1) DEFAULT NULL,
  `verbose` bit(1) DEFAULT NULL,
  `update_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rowid`)
);

CREATE TABLE IF NOT EXISTS `beacon`.`conf_hash` (
  `conf_hash` varchar(256) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `beacon`.`delta` (
  `connection_id` int DEFAULT NULL,
  `sip` varchar(256) DEFAULT NULL,
  `dip` varchar(256) DEFAULT NULL,
  `port` int DEFAULT NULL,
  `proto` varchar(256) DEFAULT NULL,
  `dt` datetime DEFAULT NULL,
  `delta_ms` float DEFAULT NULL,
  `delta_mins` float DEFAULT NULL,
  `source_file` varchar(256) DEFAULT NULL,
  `src_row_id` int DEFAULT NULL,
  `group_id` int DEFAULT NULL,
  KEY `group_id` (`group_id`),
  CONSTRAINT `delta_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `beacon_group` (`group_id`),
  CONSTRAINT `delta_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `beacon_group` (`group_id`)
);

CREATE TABLE IF NOT EXISTS  `beacon`.`raw_source` (
  `source_file` varchar(256) DEFAULT NULL,
  `count` int DEFAULT NULL,
  `group_id` int DEFAULT NULL,
  KEY `group_id` (`group_id`),
  CONSTRAINT `raw_source_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `beacon_group` (`group_id`)
);

CREATE TABLE IF NOT EXISTS  `beacon`.`time_delta` (
  `rowid` int NOT NULL AUTO_INCREMENT,
  `delta` int DEFAULT NULL,
  PRIMARY KEY (`rowid`)
);

CREATE TABLE IF NOT EXISTS `beacon`.`dns`
(`rowid` int NOT NULL AUTO_INCREMENT,
`ip` varchar(256),
`dns` varchar(256),
`create_date` datetime DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`rowid`),
CONSTRAINT `ux_dns` UNIQUE (`ip`,`dns`));

/*********************************************************************
**  Views 
*********************************************************************/

CREATE OR REPLACE DEFINER = 'root'@'localhost' 
SQL SECURITY DEFINER VIEW `beacon`.`vw_beacon`
AS 
select `bg`.`uid` AS `uid`,
`b`.`source_ip` AS `source_ip`,
`b`.`dest_ip` AS `dest_ip`,
`b`.`port` AS `port`,
ifnull(`b`.`likelihood`,0.0) AS `score`,
ifnull(`d`.`dns`,'UNKNOWN') as `dns`,
count(`b`.`uid`) AS `conn_cnt`,
min(`b`.`dt`) AS `min_dt`,
max(`b`.`dt`) AS `max_dt` 
from `beacon`.`beacon_group` `bg` 
inner join `beacon`.`beacon` `b` on
	`bg`.`group_id` = `b`.`group_id` 
left join `beacon`.`dns` d on
	`b`.`dest_ip` = `d`.`ip`
where `b`.`dest_ip` not in (select distinct `beacon_filter`.`ip` from `beacon`.`beacon_filter`) 
group by `bg`.`uid`,`b`.`source_ip`,`b`.`dest_ip`,`b`.`port`,`b`.`likelihood`,`d`.`dns`;


CREATE OR REPLACE DEFINER = 'root'@'localhost' 
SQL SECURITY DEFINER VIEW `beacon`.`vw_beacon_group` 
AS
select `bg`.`uid` AS `uid`,
`l`.`log_file` AS `log_file`,
`bg`.`dt` AS `dt`,
count(distinct `b`.`source_ip`,`b`.`port`,`b`.`dest_ip`) AS `beacons` 
from `beacon`.`beacon_group` `bg` 
left join `beacon`.`beacon` `b` on
	`bg`.`group_id` = `b`.`group_id` 
left join `beacon`.`beacon_log` `l` on
	`bg`.`group_id` = `l`.`group_id` 
where `b`.`dest_ip` not in (select distinct `beacon_filter`.`ip` from `beacon`.`beacon_filter`) 
group by `bg`.`uid`,`l`.`log_file`,`bg`.`dt`;

CREATE OR REPLACE DEFINER = 'root'@'localhost' 
SQL SECURITY DEFINER VIEW `beacon`.`vw_filtered_beacons`
as
select distinct f.ip,d.dns,f.short_desc,f.dt
from `beacon`.`beacon_filter` f
left join `beacon`.`dns` d on
	f.ip = d.ip
where f.is_user = True;

/*********************************************************************
**  PRIVILEGES 
*********************************************************************/

DROP USER IF EXISTS 'grafana'@'%';
FLUSH PRIVILEGES;

CREATE USER IF NOT EXISTS 'grafana'@'%' IDENTIFIED BY 'B3aC0nHunT!';
GRANT USAGE ON *.* TO 'grafana'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `beacon`.* TO 'grafana'@'%';
GRANT DROP, CREATE ON TABLE beacon.* TO 'grafana'@'%';

FLUSH PRIVILEGES;

/*********************************************************************
**  DATA
*********************************************************************/

insert into `beacon`.`dns`
(dns,ip)
values
('youtube.com','142.251.16.190'),
('en.wikipedia.org','208.80.154.224'),
('instagram.com','157.240.229.174'),
('facebook.com','157.240.229.35'),
('twitter.com','104.244.42.1'),
('whatsapp.com','157.240.229.60'),
('pinterest.com','151.101.64.84'),
('reddit.com','151.101.129.140'),
('play.google.com','172.253.122.102'),
('tiktok.com','18.160.18.116'),
('amazon.com','52.94.236.248'),
('microsoft.com','20.112.250.133'),
('imdb.com','52.94.237.74'),
('apple.com','17.253.144.10'),
('es.wikipedia.org','208.80.154.224'),
('espncricinfo.com','13.251.31.161'),
('globo.com','186.192.83.12'),
('de.wikipedia.org','208.80.154.224'),
('nytimes.com','151.101.193.164'),
('translate.google.com','142.251.179.139'),
('fandom.com','199.232.212.194'),
('cricbuzz.com','35.200.167.142'),
('fr.wikipedia.org','208.80.154.224'),
('quora.com','52.5.255.219'),
('yahoo.co.jp','183.79.249.124'),
('netflix.com','3.230.129.93'),
('linkedin.com','13.107.42.14'),
('ja.wikipedia.org','208.80.154.224'),
('canva.com','104.16.103.112'),
('ru.wikipedia.org','208.80.154.224'),
('mayoclinic.org','129.176.1.88'),
('it.wikipedia.org','208.80.154.224'),
('amazon.in','52.95.116.115'),
('openai.com','172.64.154.211'),
('espn.com','18.165.83.78'),
('indeed.com','162.159.130.67'),
('bbc.co.uk','151.101.0.81'),
('pt.wikipedia.org','208.80.154.224'),
('roblox.com','128.116.99.3'),
('adobe.com','23.46.15.18'),
('webmd.com','207.231.204.56'),
('speedtest.net','151.101.66.219'),
('nih.gov','156.40.212.210'),
('yelp.com','146.75.32.116'),
('amazon.co.jp','52.119.168.48'),
('healthline.com','3.162.103.84'),
('indiatimes.com','23.1.57.205'),
('amazon.de','54.239.39.102'),
('flipkart.com','103.243.32.90'),
('accuweather.com','104.86.80.19'),
('zh.wikipedia.org','208.80.154.224'),
('tripadvisor.com','151.101.66.28'),
('samsung.com','211.45.27.231'),
('ikea.com','173.223.153.206'),
('investing.com','104.18.26.183'),
('etsy.com','151.101.65.224'),
('cookpad.com','151.101.193.55'),
('ndtv.com','96.7.18.47'),
('clevelandclinic.org','172.64.155.161'),
('bbc.com','151.101.0.81'),
('amazon.co.uk','54.239.34.171'),
('mail.yahoo.com','69.147.92.12'),
('hindustantimes.com','23.39.184.250'),
('weather.com','23.47.27.153'),
('booking.com','108.138.64.67'),
('slideshare.net','151.101.66.152'),
('steampowered.com','23.213.69.147'),
('pl.wikipedia.org','208.80.154.224'),
('id.wikipedia.org','208.80.154.224'),
('britannica.com','3.211.121.27'),
('spotify.com','35.186.224.24'),
('moneycontrol.com','23.205.105.6'),
('support.google.com','142.250.31.100'),
('medlineplus.gov','99.84.208.54'),
('ar.wikipedia.org','208.80.154.224'),
('walmart.com','23.220.132.133'),
('merriam-webster.com','3.162.112.64'),
('eci.gov.in','164.100.229.115'),
('forbes.com','151.101.66.49'),
('tr.wikipedia.org','208.80.154.224'),
('medicalnewstoday.com','13.32.151.80'),
('nike.com','18.160.18.65'),
('www.gov.uk','146.75.28.144'),
('ebay.com','23.212.251.9'),
('kompas.com','13.249.39.7'),
('mlb.com','34.102.163.158'),
('homedepot.com','35.201.95.83'),
('cambridge.org','104.17.111.190'),
('wise.com','104.18.39.116'),
('goal.com','99.80.140.55'),
('allrecipes.com','151.101.66.137'),
('www.nhs.uk','184.87.190.150'),
('github.com','140.82.114.4'),
('nl.wikipedia.org','208.80.154.224'),
('amazon.fr','52.95.116.113'),
('wiktionary.org','208.80.154.224'),
('indianexpress.com','23.220.129.72'),
('skysports.com','90.216.128.5'),
('smallpdf.com','18.160.10.69'),
('turkiye.gov.tr','94.55.118.33'),
('finance.yahoo.com','69.147.92.11'),
('hi.wikipedia.org','208.80.154.224'),
('chatgpt.com','104.18.32.115'),
('discord.com','162.159.137.232'),
('thehindu.com','104.18.39.235'),
('amazon.es','54.239.33.90'),
('365scores.com','18.160.41.110'),
('yahoo.com','74.6.143.26'),
('nba.com','54.68.182.72'),
('twitch.tv','151.101.130.167'),
('cnn.com','151.101.3.5'),
('google.com','142.251.111.100'),
('shutterstock.com','75.2.58.105'),
('hollywoodbets.net','172.64.147.200'),
('target.com','151.101.2.187'),
('paypal.com','192.229.210.155'),
('huawei.com','121.37.49.12'),
('primevideo.com','18.160.46.102'),
('investopedia.com','151.101.194.137'),
('www.gov.br','161.148.164.31'),
('aliexpress.com','47.246.173.30'),
('rottentomatoes.com','23.9.179.148'),
('tradingview.com','3.162.103.100'),
('telegram.org','149.154.167.99'),
('playstation.com','52.52.162.169'),
('trustpilot.com','54.155.240.248'),
('ca.wikipedia.org','208.80.154.224'),
('news18.com','23.205.105.42'),
('lowes.com','23.220.132.119'),
('cvs.com','103.224.182.246'),
('baidu.com','110.242.68.66'),
('live.com','204.79.197.212'),
('duckduckgo.com','52.149.246.39'),
('sharepoint.com','13.107.9.168'),
('craigslist.com','208.82.238.135'),
('venmo.com','52.84.150.50'),
('cashapp.com','76.223.105.230'),
('nfl.com','151.101.193.153'),
('nhl.com','104.18.17.236'),
('cvs.com','23.62.161.242'),
('fandango.com','2.17.188.84');

insert into `beacon`.`beacon_filter`
(ip,short_desc,is_user)
select distinct ip,'Default',False from `beacon`.`dns`
where ip != '2.17.188.84';
