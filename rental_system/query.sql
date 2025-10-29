create database rental_system;
use rental_system

CREATE TABLE tenants (
id INT AUTO_INCREMENT PRIMARY KEY AUTO_INCREMENT,
name VARCHAR(255),
address VARCHAR(255),
contact_number INT(10));

CREATE TABLE payments (
id INT AUTO_INCREMENT PRIMARY KEY,
tenant_id INT,
amount FLOAT,
payment_date DATE,
status VARCHAR(10),
amount_paid FLOAT,
Pending_amount FLOAT,
advance_amount FLOAT,
FOREIGN KEY (tenant_id) REFERENCES tenants(id));
