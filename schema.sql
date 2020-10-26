CREATE TABLE IF NOT EXISTS words (
    word VARCHAR NOT NULL,
    document_id BIGINT NOT NULL,
    count INT NOT NULL
);

CREATE INDEX idx_words_word ON words (word);
CREATE INDEX idx_words_id ON words(document_id);