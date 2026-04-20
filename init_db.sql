CREATE DATABASE IF NOT EXISTS fixture;
USE fixture;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS partidos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    equipo_local VARCHAR(50) NOT NULL,
    equipo_visitante VARCHAR(50) NOT NULL,
    fecha DATETIME NOT NULL,
    fase VARCHAR(50) NOT NULL,
    estadio VARCHAR(50) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    local INT,
    visitante INT
);

CREATE TABLE IF NOT EXISTS predicciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_partido INT NOT NULL,
    local INT NOT NULL,
    visitante INT NOT NULL,
    puntos INT DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_partido) REFERENCES partidos(id),
    UNIQUE (id_usuario, id_partido)
);