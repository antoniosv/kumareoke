drop table if exists song;
create table song(
       id integer primary key autoincrement,
       title text not null,
       ip varchar(20)
);
