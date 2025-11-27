-- Create databases for all microservices
CREATE DATABASE IF NOT EXISTS auth_db;
CREATE DATABASE IF NOT EXISTS user_db;
CREATE DATABASE IF NOT EXISTS device_db;
CREATE DATABASE IF NOT EXISTS monitoring_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE user_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE device_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE monitoring_db TO postgres;
