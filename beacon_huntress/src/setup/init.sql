CREATE DATABASE IF NOT EXISTS beacon;

CREATE TABLE IF NOT EXISTS `beacon`.`beacon` (
   `uid` varchar(256) DEFAULT NULL,
   `orig_bytes` float DEFAULT NULL,
   `source_ip` varchar(256) DEFAULT NULL,
   `source_port` int DEFAULT NULL,
   `port` int DEFAULT NULL,
   `dest_ip` varchar(256) DEFAULT NULL,
   `local_resp` tinyint(1) DEFAULT NULL,
   `missed_bytes` float DEFAULT NULL,
   `orig_pkts` int DEFAULT NULL,
   `orig_ip_bytes` int DEFAULT NULL,
   `community_id` varchar(256) DEFAULT NULL,
   `ts` float DEFAULT NULL,
   `proto` varchar(256) DEFAULT NULL,
   `duration` float DEFAULT NULL,
   `resp_ip_bytes` int DEFAULT NULL,
   `local_orig` tinyint(1) DEFAULT NULL,
   `service` varchar(256) DEFAULT NULL,
   `resp_pkts` int DEFAULT NULL,
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
   `dt` datetime DEFAULT NULL
 );

select if ( 
    exists( 
        select distinct index_name from information_schema.statistics  
        where table_schema = 'beacon'
        and `table_name` = 'beacon' and index_name like 'ux_beacon'
    ) 
    ,'select ''index ux_beacon exists'' val;'
    ,'CREATE UNIQUE INDEX ux_beacon ON beacon.beacon (`source_file`,`src_row_id`)') into @a; 
PREPARE ux_beacon FROM @a; 
EXECUTE ux_beacon; 
DEALLOCATE PREPARE ux_beacon; 

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
   `src_row_id` int DEFAULT NULL
 );

 select if ( 
    exists( 
        select distinct index_name from information_schema.statistics  
        where table_schema = 'beacon'
        and `table_name` = 'delta' and index_name like 'ux_delta'
    ) 
    ,'select ''index ux_delta exists'' val;'
    ,'CREATE UNIQUE INDEX ux_delta ON beacon.delta (`source_file`,`src_row_id`)') into @a; 
PREPARE ux_delta FROM @a; 
EXECUTE ux_delta; 
DEALLOCATE PREPARE ux_delta; 


CREATE TABLE IF NOT EXISTS `beacon`.`raw_source` (
   `source_file` varchar(256) DEFAULT NULL,
   `count` int DEFAULT NULL
 );

 select if ( 
    exists( 
        select distinct index_name from information_schema.statistics  
        where table_schema = 'beacon'
        and `table_name` = 'raw_source' and index_name like 'ux_raw_source'
    ) 
    ,'select ''index ux_delta exists'' val;'
    ,'CREATE UNIQUE INDEX ux_raw_source ON beacon.raw_source (`source_file`,`count`)') into @a; 
PREPARE ux_beacon FROM @a; 
EXECUTE ux_beacon; 
DEALLOCATE PREPARE ux_beacon; 

CREATE TABLE IF NOT EXISTS  `beacon`.`conf_hash`
(conf_hash varchar(256));

CREATE TABLE IF NOT EXISTS `beacon`.`beacon_filter` (
   `ip` varchar(256) PRIMARY KEY
 );


DROP USER IF EXISTS 'grafana'@'%';
FLUSH PRIVILEGES;

CREATE USER IF NOT EXISTS 'grafana'@'%' IDENTIFIED BY 'BeaconHunt1!';
GRANT USAGE ON *.* TO 'grafana'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON `beacon`.* TO `grafana`@`%`;
GRANT DROP ON TABLE beacon.* TO 'grafana'@'%';
FLUSH PRIVILEGES;