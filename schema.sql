CREATE TABLE IF NOT EXISTS words (
    word VARCHAR NOT NULL,
    document_id BIGINT NOT NULL,
    count INT NOT NULL
);