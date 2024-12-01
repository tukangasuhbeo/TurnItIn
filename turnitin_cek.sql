show databases;
create database turnitin_cek;
use turnitin_cek;
show tables;

CREATE TABLE Articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title text NOT NULL,
    author VARCHAR(255),
    content text,
    turnitin_score float not null
) Engine = InnoDB;


# UPDATE UPDATE TABLE STATUS #
ALTER TABLE Articles
modify COLUMN turnitin_result VARCHAR(50);

alter table Articles
modify column id int not NULL auto_increment;

desc Articles;
alter table Articles
modify column turnitin_score float null;


CREATE TABLE UncheckedTitles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
)Engine = InnoDB;


### liat hasil turnitin ###
SHOW TRIGGERS;
select* from Articles;
truncate table Articles;




ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Ranggam04@';
FLUSH PRIVILEGES;


#uodate localhost for user
SHOW VARIABLES LIKE 'local_infile';
SHOW GRANTS FOR 'root'@'localhost';

