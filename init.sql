create table users(
    id serial, 
    username varchar(20) not null,
    pwd varchar(25) not null,
    pwd_reset_token varchar(100) not null,
    pwd_reset_expiration datetime
)

