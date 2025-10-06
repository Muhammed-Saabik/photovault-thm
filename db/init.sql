CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE secrets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  value TEXT
);

INSERT INTO users (username, password_hash, role) VALUES
('alice', 'password123-hashplaceholder', 'user'),
('bob', 'password123-hashplaceholder', 'user'),
('admin', 'admin-pass-hashplaceholder', 'admin');

INSERT INTO secrets (name, value) VALUES
('sql_flag', 'FLAG{THM-SQL-PLACEHOLDER}'),
('crypto_flag', 'ENCRYPTED_PLACEHOLDER'),
('bac_flag', 'FLAG{THM-BAC-PLACEHOLDER}');
