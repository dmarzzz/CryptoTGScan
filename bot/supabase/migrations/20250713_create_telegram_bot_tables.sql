-- Telegram Bot Database Schema V1
-- Created: 2025-07-13
-- Purpose: Store Telegram messages, users, chats, and forum topics

-- Enable UUID extension for future use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table - Store Telegram user information
CREATE TABLE users_v1 (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(32),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    is_bot BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    language_code VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Chats Table - Store information about groups, supergroups, and channels
CREATE TABLE chats_v1 (
    chat_id BIGINT PRIMARY KEY,
    chat_type VARCHAR(20) NOT NULL, -- 'private', 'group', 'supergroup', 'channel'
    title VARCHAR(255),
    username VARCHAR(32),
    description TEXT,
    is_forum BOOLEAN DEFAULT FALSE,
    member_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT chat_type_check CHECK (chat_type IN ('private', 'group', 'supergroup', 'channel'))
);

-- 3. Forum Topics Table - For supergroups with forum mode enabled
CREATE TABLE forum_topics_v1 (
    topic_id INTEGER NOT NULL,
    chat_id BIGINT NOT NULL,
    name VARCHAR(128) NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (chat_id, topic_id),
    FOREIGN KEY (chat_id) REFERENCES chats_v1(chat_id) ON DELETE CASCADE
);

-- 4. Messages Table - Main table storing all messages
CREATE TABLE messages_v1 (
    id BIGSERIAL PRIMARY KEY,
    telegram_message_id INTEGER NOT NULL,
    chat_id BIGINT NOT NULL,
    from_user_id BIGINT,
    message_thread_id INTEGER, -- For forum topics
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    edit_date TIMESTAMP WITH TIME ZONE,
    text TEXT,
    message_type VARCHAR(50) DEFAULT 'text', -- 'text', 'photo', 'video', etc.
    reply_to_message_id INTEGER, -- ID of the message being replied to
    reply_to_chat_id BIGINT, -- Chat ID if replying to a message from another chat
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (chat_id) REFERENCES chats_v1(chat_id) ON DELETE CASCADE,
    FOREIGN KEY (from_user_id) REFERENCES users_v1(user_id),
    FOREIGN KEY (reply_to_chat_id) REFERENCES chats_v1(chat_id),
    UNIQUE(chat_id, telegram_message_id)
);

-- Create indexes for better performance
CREATE INDEX idx_messages_v1_chat_date ON messages_v1(chat_id, date DESC);
CREATE INDEX idx_messages_v1_user ON messages_v1(from_user_id);
CREATE INDEX idx_messages_v1_thread ON messages_v1(chat_id, message_thread_id);
CREATE INDEX idx_messages_v1_reply ON messages_v1(reply_to_message_id);
CREATE INDEX idx_messages_v1_type ON messages_v1(message_type);
CREATE INDEX idx_messages_v1_created ON messages_v1(created_at DESC);

CREATE INDEX idx_users_v1_username ON users_v1(username);
CREATE INDEX idx_chats_v1_type ON chats_v1(chat_type);
CREATE INDEX idx_chats_v1_forum ON chats_v1(is_forum);

-- Create update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update timestamp triggers
CREATE TRIGGER update_users_v1_updated_at BEFORE UPDATE ON users_v1
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chats_v1_updated_at BEFORE UPDATE ON chats_v1
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users_v1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats_v1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE forum_topics_v1 ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages_v1 ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all operations for now - you can restrict later)
CREATE POLICY "Allow all operations on users_v1" ON users_v1
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on chats_v1" ON chats_v1
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on forum_topics_v1" ON forum_topics_v1
    FOR ALL USING (true);

CREATE POLICY "Allow all operations on messages_v1" ON messages_v1
    FOR ALL USING (true);

-- Add comments for documentation
COMMENT ON TABLE users_v1 IS 'Stores Telegram user information - V1';
COMMENT ON TABLE chats_v1 IS 'Stores information about Telegram chats, groups, supergroups, and channels - V1';
COMMENT ON TABLE forum_topics_v1 IS 'Stores forum topics for supergroups with forum mode enabled - V1';
COMMENT ON TABLE messages_v1 IS 'Main messages table storing all message metadata - V1';
COMMENT ON COLUMN messages_v1.telegram_message_id IS 'Original message ID from Telegram (not unique across chats)';
COMMENT ON COLUMN messages_v1.message_thread_id IS 'For forum topics: the topic ID; for replies: the original message ID'; 