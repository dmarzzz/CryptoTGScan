# Telegram Bot Database Documentation

## 📊 Database Schema V1

This document describes the database schema for the Telegram bot, designed to store messages, users, chats, and forum topics from Telegram.

## 🗂️ Table Structure

### 1. Users Table (`users_v1`)

Stores information about Telegram users who interact with the bot.

```sql
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
```

**Columns:**
- `user_id`: Telegram user ID (primary key)
- `username`: Optional username without @
- `first_name`: User's first name (required)
- `last_name`: User's last name (optional)
- `is_bot`: Whether the user is a bot
- `is_premium`: Whether the user has Telegram Premium
- `language_code`: User's language code (e.g., 'en', 'es')
- `created_at`: When the user was first recorded
- `updated_at`: When the user was last updated

### 2. Chats Table (`chats_v1`)

Stores information about Telegram chats, groups, supergroups, and channels.

```sql
CREATE TABLE chats_v1 (
    chat_id BIGINT PRIMARY KEY,
    chat_type VARCHAR(20) NOT NULL,
    title VARCHAR(255),
    username VARCHAR(32),
    description TEXT,
    is_forum BOOLEAN DEFAULT FALSE,
    member_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT chat_type_check CHECK (chat_type IN ('private', 'group', 'supergroup', 'channel'))
);
```

**Columns:**
- `chat_id`: Telegram chat ID (primary key, negative for groups/channels)
- `chat_type`: Type of chat ('private', 'group', 'supergroup', 'channel')
- `title`: Chat title/name
- `username`: Public username for public chats
- `description`: Chat description
- `is_forum`: Whether the supergroup has forum mode enabled
- `member_count`: Number of members in the chat
- `created_at`: When the chat was first recorded
- `updated_at`: When the chat was last updated

### 3. Forum Topics Table (`forum_topics_v1`)

Stores forum topics for supergroups with forum mode enabled.

```sql
CREATE TABLE forum_topics_v1 (
    topic_id INTEGER NOT NULL,
    chat_id BIGINT NOT NULL,
    name VARCHAR(128) NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (chat_id, topic_id),
    FOREIGN KEY (chat_id) REFERENCES chats_v1(chat_id) ON DELETE CASCADE
);
```

**Columns:**
- `topic_id`: Topic ID (same as the message ID that created the topic)
- `chat_id`: Chat ID where the topic exists
- `name`: Topic name
- `is_closed`: Whether the topic is closed
- `created_at`: When the topic was created

### 4. Messages Table (`messages_v1`)

Main table storing all message metadata and content.

```sql
CREATE TABLE messages_v1 (
    id BIGSERIAL PRIMARY KEY,
    telegram_message_id INTEGER NOT NULL,
    chat_id BIGINT NOT NULL,
    from_user_id BIGINT,
    message_thread_id INTEGER,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    edit_date TIMESTAMP WITH TIME ZONE,
    text TEXT,
    message_type VARCHAR(50) DEFAULT 'text',
    reply_to_message_id INTEGER,
    reply_to_chat_id BIGINT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (chat_id) REFERENCES chats_v1(chat_id) ON DELETE CASCADE,
    FOREIGN KEY (from_user_id) REFERENCES users_v1(user_id),
    FOREIGN KEY (reply_to_chat_id) REFERENCES chats_v1(chat_id),
    UNIQUE(chat_id, telegram_message_id)
);
```

**Columns:**
- `id`: Auto-incrementing primary key
- `telegram_message_id`: Original Telegram message ID
- `chat_id`: Chat where the message was sent
- `from_user_id`: User who sent the message (NULL for channel posts)
- `message_thread_id`: For forum topics: topic ID; for replies: original message ID
- `date`: When the message was sent (Telegram timestamp)
- `edit_date`: When the message was last edited
- `text`: Message text content
- `message_type`: Type of message ('text', 'photo', 'video', etc.)
- `reply_to_message_id`: ID of the message being replied to
- `reply_to_chat_id`: Chat ID if replying to a message from another chat
- `is_deleted`: Whether the message was deleted
- `created_at`: When the message was recorded in our database

## 🔗 Relationships

- **users_v1** ←→ **messages_v1**: One user can send many messages
- **chats_v1** ←→ **messages_v1**: One chat can have many messages
- **chats_v1** ←→ **forum_topics_v1**: One chat can have many forum topics
- **messages_v1** ←→ **messages_v1**: Messages can reply to other messages

## 📈 Indexes

Performance indexes have been created for common queries:

```sql
-- Message indexes
CREATE INDEX idx_messages_v1_chat_date ON messages_v1(chat_id, date DESC);
CREATE INDEX idx_messages_v1_user ON messages_v1(from_user_id);
CREATE INDEX idx_messages_v1_thread ON messages_v1(chat_id, message_thread_id);
CREATE INDEX idx_messages_v1_reply ON messages_v1(reply_to_message_id);
CREATE INDEX idx_messages_v1_type ON messages_v1(message_type);
CREATE INDEX idx_messages_v1_created ON messages_v1(created_at DESC);

-- User indexes
CREATE INDEX idx_users_v1_username ON users_v1(username);

-- Chat indexes
CREATE INDEX idx_chats_v1_type ON chats_v1(chat_type);
CREATE INDEX idx_chats_v1_forum ON chats_v1(is_forum);
```

## 🔧 Database Commands

### Migration Commands

```bash
# Apply migrations to remote database
supabase db push

# Reset local database
supabase db reset

# Generate new migration
supabase migration new migration_name

# View migration status
supabase migration list
```

### Common SQL Queries

#### Get Recent Messages from a Chat
```sql
SELECT 
    m.text,
    m.date,
    u.first_name,
    u.username,
    c.title as chat_title
FROM messages_v1 m
JOIN users_v1 u ON m.from_user_id = u.user_id
JOIN chats_v1 c ON m.chat_id = c.chat_id
WHERE m.chat_id = -1001234567890
ORDER BY m.date DESC
LIMIT 50;
```

#### Get User Activity
```sql
SELECT 
    u.first_name,
    u.username,
    COUNT(*) as message_count,
    MAX(m.date) as last_message
FROM messages_v1 m
JOIN users_v1 u ON m.from_user_id = u.user_id
WHERE m.chat_id = -1001234567890
GROUP BY u.user_id, u.first_name, u.username
ORDER BY message_count DESC;
```

#### Get Forum Topics
```sql
SELECT 
    ft.name,
    ft.is_closed,
    COUNT(m.id) as message_count
FROM forum_topics_v1 ft
LEFT JOIN messages_v1 m ON ft.chat_id = m.chat_id AND ft.topic_id = m.message_thread_id
WHERE ft.chat_id = -1001234567890
GROUP BY ft.topic_id, ft.name, ft.is_closed
ORDER BY message_count DESC;
```

#### Get Reply Chains
```sql
WITH RECURSIVE reply_chain AS (
    SELECT 
        m.id,
        m.telegram_message_id,
        m.text,
        m.from_user_id,
        m.reply_to_message_id,
        1 as depth
    FROM messages_v1 m
    WHERE m.telegram_message_id = 12345
    
    UNION ALL
    
    SELECT 
        m.id,
        m.telegram_message_id,
        m.text,
        m.from_user_id,
        m.reply_to_message_id,
        rc.depth + 1
    FROM messages_v1 m
    JOIN reply_chain rc ON m.telegram_message_id = rc.reply_to_message_id
    WHERE rc.depth < 10
)
SELECT * FROM reply_chain ORDER BY depth;
```

## 🚀 Usage in Bot Code

### Inserting a User
```typescript
const { error } = await supabase
  .from('users_v1')
  .upsert({
    user_id: ctx.from.id,
    username: ctx.from.username,
    first_name: ctx.from.first_name,
    last_name: ctx.from.last_name,
    is_bot: ctx.from.is_bot,
    is_premium: ctx.from.is_premium,
    language_code: ctx.from.language_code
  }, {
    onConflict: 'user_id'
  });
```

### Inserting a Chat
```typescript
const { error } = await supabase
  .from('chats_v1')
  .upsert({
    chat_id: ctx.chat.id,
    chat_type: ctx.chat.type,
    title: ctx.chat.title,
    username: ctx.chat.username,
    description: ctx.chat.description,
    is_forum: ctx.chat.is_forum,
    member_count: ctx.chat.member_count
  }, {
    onConflict: 'chat_id'
  });
```

### Inserting a Message
```typescript
const { error } = await supabase
  .from('messages_v1')
  .insert({
    telegram_message_id: ctx.message.message_id,
    chat_id: ctx.chat.id,
    from_user_id: ctx.from?.id,
    message_thread_id: ctx.message.message_thread_id,
    date: new Date(ctx.message.date * 1000),
    edit_date: ctx.message.edit_date ? new Date(ctx.message.edit_date * 1000) : null,
    text: ctx.message.text,
    message_type: 'text',
    reply_to_message_id: ctx.message.reply_to_message?.message_id,
    reply_to_chat_id: ctx.message.reply_to_message?.chat?.id
  });
```

## 🔒 Security

- **Row Level Security (RLS)** is enabled on all tables
- **Policies** currently allow all operations (can be restricted later)
- **Foreign key constraints** ensure data integrity
- **Unique constraints** prevent duplicate records

## 📝 Notes

- All tables have `_v1` suffix for future migration support
- Timestamps are stored in UTC
- Telegram message IDs are not unique across chats
- Forum topics use the same ID as the message that created them
- Reply tracking supports cross-chat replies

## 🔄 Future Migrations

When creating V2 of the schema:

1. Create new tables with `_v2` suffix
2. Write migration script to copy data from V1 to V2
3. Update bot code to use V2 tables
4. Keep V1 tables for backup/reference

Example migration:
```sql
-- Create V2 tables
CREATE TABLE messages_v2 AS SELECT * FROM messages_v1;

-- Add new columns
ALTER TABLE messages_v2 ADD COLUMN new_feature VARCHAR(255);

-- Update bot to use V2 tables
-- Eventually drop V1 tables when no longer needed
``` 