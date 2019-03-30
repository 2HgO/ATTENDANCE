create database AI_4;
use AI_4;
create table class(
    id int(10) unsigned not null auto_increment primary key,
    Matric char(7) not null unique,
    FName varchar(20) not null default '',
    LName varchar(20) not null default '',
    Attendance int(10) not null default 0
);