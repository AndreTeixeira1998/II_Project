CREATE SCHEMA FACTORY AUTHORIZATION ii;
SET search_path TO FACTORY;

CREATE TYPE order_state AS ENUM ('active', 'inactive', 'pending', 'cancelled', 'aborted');
CREATE TYPE piece_type AS ENUM('P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9');

SET timezone = 'Europe/Lisbon';