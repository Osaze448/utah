-- ============================================================
-- VERITAS MICROFINANCE BANK - Database Initialization
-- Runs automatically when the Oracle Database container is created
-- ============================================================

-- Ensure we are in the default Pluggable Database (FREEPDB1)
-- (The official 23c Free container usually runs startup scripts directly in the PDB)
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Create the application schema user
CREATE USER veritas_admin IDENTIFIED BY "VeritasDB@2024";

-- Grant standard role privileges for development
GRANT CONNECT, RESOURCE, DBA TO veritas_admin;

-- Set default tablespace and quota
ALTER USER veritas_admin DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS;
