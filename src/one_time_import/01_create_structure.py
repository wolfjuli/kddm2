from db_helper import *

sql = """
DROP TABLE IF EXISTS `failed`;
CREATE TABLE `failed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `filename` text,
  `errortext` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=428 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `from_to_mail`;
CREATE TABLE `from_to_mail` (
  `from` varchar(200) NOT NULL,
  `to` varchar(200) NOT NULL,
  `mailId` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mail_paragraphs`;
CREATE TABLE `mail_paragraphs` (
  `mailId` int(11) DEFAULT NULL,
  `sha` varchar(200) DEFAULT NULL,
  `sortorder` int(11) DEFAULT NULL,
  deleted int DEFAULT 0
  pid int,
  KEY `iddx_mail_paragraph_mailId` (`mailId`),
  KEY `mail_paragraphs_sha_index` (`sha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `mails`;
CREATE TABLE `mails` (
  `id` int(11) NOT NULL,
  `body` longtext,
  `x-cc` longtext,
  `from` longtext,
  `subject` longtext,
  `x-folder` longtext,
  `content-transfer-encoding` longtext,
  `x-bcc` longtext,
  `filepath` longtext,
  `to` longtext,
  `x-origin` longtext,
  `x-filename` longtext,
  `x-from` longtext,
  `date` longtext,
  `x-to` longtext,
  `message-id` longtext,
  `content-type` longtext,
  `mime-version` longtext,
  `cc` longtext,
  `bcc` longtext,
  `attendees` longtext,
  `re` longtext,
  `time` longtext,
  `conference room` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `sha_paragraphs`;
CREATE TABLE `sha_paragraphs` (
  `sha` varchar(200) NOT NULL,
  `paragraph` longtext,
  id int,
  PRIMARY KEY (`sha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
"""

cursor = getCursor()
execute(cursor, sql, True)
