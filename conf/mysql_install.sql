CREATE USER '%(db_user)s'@'localhost' IDENTIFIED BY "%(db_pass)s";
GRANT USAGE ON * . * TO '%(db_user)s'@'localhost' IDENTIFIED BY "%(db_pass)s" WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0 ;
CREATE DATABASE IF NOT EXISTS `%(db_name)s` ;
GRANT ALL PRIVILEGES ON `%(db_name)s` . * TO '%(db_user)s'@'localhost';
