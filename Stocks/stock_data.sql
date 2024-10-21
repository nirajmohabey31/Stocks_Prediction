CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    stock_symbol VARCHAR(10),
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT
);

SELECT * FROM stock_data LIMIT 10;
SELECT COUNT(*) FROM stock_data;
SELECT DISTINCT stock_symbol FROM stock_data;