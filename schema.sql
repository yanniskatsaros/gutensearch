CREATE TABLE IF NOT EXISTS words (
    word VARCHAR NOT NULL,
    document_id BIGINT NOT NULL,
    count INT NOT NULL
);

CREATE TABLE IF NOT EXISTS distinct_words (
    word VARCHAR NOT NULL
);