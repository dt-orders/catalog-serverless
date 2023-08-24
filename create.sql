create database catalog;

CREATE TABLE IF NOT EXISTS catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

insert into catalog(name,price) values("iPod", 20.00);
insert into catalog(name,price) values("iPod touch", 10.00);
insert into catalog(name,price) values("iPad", 400.00);
insert into catalog(name,price) values("iPhone 42", 50000.00);

