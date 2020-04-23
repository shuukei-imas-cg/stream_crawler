CREATE TABLE `cg9th` (
  `tweet_id` bigint(20) unsigned NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  `screen_name` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `text` mediumtext NOT NULL,
  `source` varchar(255) NOT NULL,
  `source_url` varchar(255) NOT NULL,
  `idol_id` int(11) NOT NULL,
  `idol` varchar(16) NOT NULL,
  `mode` int(11) NOT NULL,
  `title` int(11) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`tweet_id`),
  UNIQUE KEY `cg9th_tweet_id_uindex` (`tweet_id`),
  KEY `cg9th_idol_id_index` (`idol_id`),
  KEY `cg9th_user_id_index` (`user_id`),
  KEY `cg9th_mode_index` (`mode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
