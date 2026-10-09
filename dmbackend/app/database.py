import os
import sqlite3


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)


DATABASE_DIR = os.path.join(
    BASE_DIR,
    "data"
)


DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "autosar.db"
)


def get_database_path():
    return DATABASE_PATH


def get_db():
    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def column_exists(
    connection,
    table_name,
    column_name
):
    result = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        row["name"] == column_name
        for row in result
    )


def init_db():
    connection = get_db()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email);


            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                original_filename TEXT NOT NULL,

                stored_filename TEXT NOT NULL,

                storage_path TEXT NOT NULL,

                extracted_text_path TEXT,

                extracted_pages_path TEXT,

                file_size INTEGER NOT NULL,

                page_count INTEGER NOT NULL DEFAULT 0,

                extracted_text_length INTEGER NOT NULL DEFAULT 0,

                status TEXT NOT NULL DEFAULT 'uploaded',

                error_message TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            CREATE INDEX IF NOT EXISTS idx_documents_user_id
            ON documents(user_id);


            CREATE INDEX IF NOT EXISTS idx_documents_status
            ON documents(status);


            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                document_id INTEGER NOT NULL,

                user_id INTEGER NOT NULL,

                chunk_index INTEGER NOT NULL,

                page_number INTEGER,

                section_title TEXT,

                chunking_strategy TEXT NOT NULL,

                chunk_size INTEGER,

                chunk_overlap INTEGER,

                text TEXT NOT NULL,

                character_count INTEGER NOT NULL,

                token_count INTEGER,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );


            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks(document_id);


            CREATE INDEX IF NOT EXISTS idx_chunks_user_id
            ON chunks(user_id);


            CREATE INDEX IF NOT EXISTS idx_chunks_strategy
            ON chunks(chunking_strategy);

            CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    chunk_id INTEGER NOT NULL,

    document_id INTEGER NOT NULL,

    user_id INTEGER NOT NULL,

    chunking_strategy TEXT NOT NULL,

    embedding_model TEXT NOT NULL,

    embedding_dimension INTEGER NOT NULL,

    vector_path TEXT NOT NULL,

    created_at TEXT NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chunk_id)
        REFERENCES chunks(id)
        ON DELETE CASCADE,

    FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id
ON embeddings(chunk_id);


CREATE INDEX IF NOT EXISTS idx_embeddings_document_id
ON embeddings(document_id);


CREATE INDEX IF NOT EXISTS idx_embeddings_model
ON embeddings(embedding_model);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT 'New conversation',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id
ON conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
ON conversations(updated_at);


CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations_json TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_user_id
ON messages(user_id);
            """
        )


        # Migration for databases created
        # before extracted_pages_path existed.
        if not column_exists(
            connection,
            "documents",
            "extracted_pages_path"
        ):
            connection.execute(
                """
                ALTER TABLE documents
                ADD COLUMN extracted_pages_path TEXT
                """
            )


        connection.commit()

    finally:
        connection.close()