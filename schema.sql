drop table if exists entries;   -- посты 
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  lake integer not null,
  dizlake integer not null,
  id_polzovatelya text not null,
  vreamya datetime not null
);

drop table if exists zik;  -- пользователи
create table zik (
  id integer primary key autoincrement,
  login text not null,
  pass text not null
);

drop table if exists dryzia;
create table dryzia (
  id integer primary key autoincrement,
  polzovatel text not null,
  dryg text not null
);

drop table if exists podpiski;
create table podpiski (
  id integer primary key autoincrement,
  kto text not null,
  komy text not null
);



drop table if exists kol_lak;
create table kol_lak (
  id integer primary key autoincrement,
  post integer not null,
  polzovatel text not null,
  lake integer  not  null,
  dizlake integer  not  null
);