-- ************************************** `Users`
CREATE TABLE IF NOT EXISTS `Users`
(
 `ssn`        varchar(9) NOT NULL ,
 `first_name` varchar(45) NOT NULL ,
 `last_name`  varchar(45) NOT NULL ,

PRIMARY KEY (`ssn`)
);


-- ************************************** `Accounts`
CREATE TABLE IF NOT EXISTS `Accounts`
(
 `number`    varchar(16) NOT NULL ,
 `pin`       varchar(4) NOT NULL ,
 `user_ssn` varchar(9) NOT NULL ,
 `balance` double NOT NULL DEFAULT 0,

PRIMARY KEY (`number`),
KEY `fkIdx_11` (`user_ssn`),
CONSTRAINT `FK_10` FOREIGN KEY `fkIdx_11` (`user_ssn`) REFERENCES `Users` (`ssn`) ON DELETE CASCADE ON UPDATE CASCADE
);