#!/usr/bin/env python3
from string import punctuation

from mail_functions import *

import pickle


sql = """

-- MySQL dump 10.13  Distrib 5.7.17, for Linux (x86_64)
--
-- Host: localhost    Database: kddm2
-- ------------------------------------------------------
-- Server version	5.7.17-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `failed`
--

DROP TABLE IF EXISTS `failed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `failed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `filename` text,
  `errortext` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=428 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `from_to_mail`
--

DROP TABLE IF EXISTS `from_to_mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `from_to_mail` (
  `from` varchar(200) NOT NULL,
  `to` varchar(200) NOT NULL,
  `mailId` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mail_paragraphs`
--

DROP TABLE IF EXISTS `mail_paragraphs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail_paragraphs` (
  `mailId` int(11) DEFAULT NULL,
  `sha` varchar(200) DEFAULT NULL,
  `sortorder` int(11) DEFAULT NULL,
  pid int,
  KEY `iddx_mail_paragraph_mailId` (`mailId`),
  KEY `mail_paragraphs_sha_index` (`sha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mails`
--

DROP TABLE IF EXISTS `mails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sha_paragraphs`
--

DROP TABLE IF EXISTS `sha_paragraphs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sha_paragraphs` (
  `sha` varchar(200) NOT NULL,
  `paragraph` longtext,
  id int,
  PRIMARY KEY (`sha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


"""

try:
    import MySQLdb
    db = MySQLdb.connect("localhost","kddm2","kddm2","kddm2")
    print("Using MySQLdb")
except:
    try:
        import pymysql
        db = pymysql.connect("localhost","kddm2","kddm2","kddm2" )
        print("Using pyMySQL")
    except:
        import pymssql
        db = pymssql.connect("localhost", "kddm2", "kddm2", "kddm2")
        print("Using pymssql")


def flush(cursor):
    db.commit()
    cursor.fetchall()
    cursor.close()
    return db.cursor()

cursor = db.cursor()

columnNames = []
cursor.execute(sql)
cursor = flush(cursor)

exit()



allFiles = getListOfFiles('../../maildir')
count = 0
columnNames = {}
parsedFiles = {}

for file in allFiles:
    count += 1

    stripedFile = stripChars(file, punctuation)
    if stripedFile in parsedFiles:
        #print "skip " + file
        continue

    parsedFiles[stripedFile] = 1

    #print "working on " + file
    parsed = getParsedContent(file)

    for key in [p.lower() for p in parsed.keys() if p.lower() not in columnNames and p != ""]:
        print("found new key " + key)
        columnNames[key.lower()] = parsed['filepath']

    if count % 10000 == 0:
        print("checked " + str(count) + " files")


with open('columnNames.pkl', 'w') as f:
    pickle.dump(columnNames, f)

print(columnNames)