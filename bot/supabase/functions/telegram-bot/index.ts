// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

console.log(`Function "telegram-bot" up and running!`)

import { Bot, webhookCallback } from 'https://deno.land/x/grammy@v1.8.3/mod.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.38.4'

// Initialize Supabase client
const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// Initialize Telegram bot
const bot = new Bot(Deno.env.get('TELEGRAM_BOT_TOKEN') || '')

// Bot commands
bot.command('start', (ctx) => ctx.reply('Welcome! Up and running.'))

bot.command('ping', (ctx) => ctx.reply(`Pong! ${new Date()} ${Date.now()}`))

// Helper function to convert Unix timestamp to ISO string
function convertUnixTimestamp(timestamp: number): string {
  return new Date(timestamp * 1000).toISOString()
}

// Helper function to check if it's a private chat
function isPrivateChat(chat: any): boolean {
  return chat?.type === 'private'
}

// Helper function to generate debug information
function generateDebugInfo(ctx: any, logEntry: any): string {
  const message = ctx.message
  const chat = ctx.chat
  const from = ctx.from
  
  const debugInfo = `
🔍 **DEBUG INFORMATION**

📱 **Message Details:**
• Message ID: ${message.message_id}
• Date: ${message.date ? convertUnixTimestamp(message.date) : 'N/A'}
• Edit Date: ${message.edit_date ? convertUnixTimestamp(message.edit_date) : 'N/A'}
• Type: ${message.text ? 'text' : 'non-text'}

👤 **User Information:**
• User ID: ${from?.id || 'N/A'}
• Username: ${from?.username || 'N/A'}
• First Name: ${from?.first_name || 'N/A'}
• Last Name: ${from?.last_name || 'N/A'}
• Is Bot: ${from?.is_bot ? 'Yes' : 'No'}
• Is Premium: ${from?.is_premium ? 'Yes' : 'No'}
• Language: ${from?.language_code || 'N/A'}

💬 **Chat Information:**
• Chat ID: ${chat?.id || 'N/A'}
• Chat Type: ${chat?.type || 'N/A'}
• Title: ${chat?.title || 'N/A'}
• Username: ${chat?.username || 'N/A'}
• Description: ${chat?.description || 'N/A'}
• Is Forum: ${chat?.is_forum ? 'Yes' : 'No'}
• Member Count: ${chat?.member_count || 'N/A'}

📝 **Message Content:**
• Text: ${message.text || 'No text'}
• Caption: ${message.caption || 'No caption'}
• Thread ID: ${message.message_thread_id || 'N/A'}

🔗 **Reply Information:**
• Reply To Message ID: ${message.reply_to_message?.message_id || 'N/A'}
• Reply To Chat ID: ${message.reply_to_message?.chat?.id || 'N/A'}

🗄️ **Database Status:**
• User Stored: ✅
• Chat Stored: ✅
• Message Stored: ✅

⏰ **Timestamps:**
• Bot Processing: ${new Date().toISOString()}
• Telegram Date: ${message.date ? convertUnixTimestamp(message.date) : 'N/A'}

🔧 **Environment:**
• Supabase URL: ${supabaseUrl ? '✅ Set' : '❌ Missing'}
• Service Key: ${supabaseServiceKey ? '✅ Set' : '❌ Missing'}
• Bot Token: ${Deno.env.get('TELEGRAM_BOT_TOKEN') ? '✅ Set' : '❌ Missing'}
• Function Secret: ${Deno.env.get('FUNCTION_SECRET') ? '✅ Set' : '❌ Missing'}
`
  
  return debugInfo
}

// Database operations
async function upsertUser(user: any): Promise<void> {
  const { error } = await supabase
    .from('users_v1')
    .upsert({
      user_id: user.id,
      username: user.username,
      first_name: user.first_name,
      last_name: user.last_name,
      is_bot: user.is_bot,
      is_premium: user.is_premium,
      language_code: user.language_code
    }, {
      onConflict: 'user_id'
    })
  
  if (error) {
    console.error('Error upserting user:', error)
  }
}

async function upsertChat(chat: any): Promise<void> {
  const { error } = await supabase
    .from('chats_v1')
    .upsert({
      chat_id: chat.id,
      chat_type: chat.type,
      title: chat.title,
      username: chat.username,
      description: chat.description,
      is_forum: chat.is_forum,
      member_count: chat.member_count
    }, {
      onConflict: 'chat_id'
    })
  
  if (error) {
    console.error('Error upserting chat:', error)
  }
}

async function insertMessage(ctx: any): Promise<void> {
  const message = ctx.message
  const chat = ctx.chat
  const from = ctx.from
  
  // Determine message type
  let messageType = 'text'
  if (message.photo) messageType = 'photo'
  else if (message.video) messageType = 'video'
  else if (message.document) messageType = 'document'
  else if (message.audio) messageType = 'audio'
  else if (message.voice) messageType = 'voice'
  else if (message.sticker) messageType = 'sticker'
  else if (message.animation) messageType = 'animation'
  
  const { error } = await supabase
    .from('messages_v1')
    .insert({
      telegram_message_id: message.message_id,
      chat_id: chat.id,
      from_user_id: from?.id,
      message_thread_id: message.message_thread_id,
      date: new Date(message.date * 1000),
      edit_date: message.edit_date ? new Date(message.edit_date * 1000) : null,
      text: message.text || message.caption || null,
      message_type: messageType,
      reply_to_message_id: message.reply_to_message?.message_id,
      reply_to_chat_id: message.reply_to_message?.chat?.id
    })
  
  if (error) {
    console.error('Error inserting message:', error)
  }
}

// Handle all text messages from channels and groups
bot.on('message:text', async (ctx) => {
  const message = ctx.message
  const chat = ctx.chat
  const from = ctx.from
  
  // Check for "vishesh" keyword (only in private chats)
  if (isPrivateChat(chat) && message.text && message.text.toLowerCase().includes('vishesh')) {
    await ctx.reply('vishesh? you mean the worlds biggest loser?')
  }
  
  // Store in database
  if (from) {
    await upsertUser(from)
  }
  await upsertChat(chat)
  await insertMessage(ctx)
  
  // Create log entry
  const logEntry = {
    timestamp: new Date().toISOString(),
    chat_id: chat?.id,
    chat_type: chat?.type,
    chat_title: chat?.title || 'Unknown',
    user_id: from?.id,
    username: from?.username || 'Unknown',
    first_name: from?.first_name || 'Unknown',
    message_text: message.text,
    message_id: message.message_id,
    date: message.date ? convertUnixTimestamp(message.date) : new Date().toISOString()
  }
  
  // Log to console (for now)
  console.log('📨 New Message:', JSON.stringify(logEntry, null, 2))
  
  // Only reply in private chats with debug information
  if (isPrivateChat(chat)) {
    const debugInfo = generateDebugInfo(ctx, logEntry)
    await ctx.reply(debugInfo)
  }
})

// Handle all non-text messages (photos, videos, documents, etc.)
bot.on('message', async (ctx) => {
  const message = ctx.message
  const chat = ctx.chat
  const from = ctx.from
  
  // Skip if it's a text message (already handled above)
  if (message.text) return
  
  // Store in database
  if (from) {
    await upsertUser(from)
  }
  await upsertChat(chat)
  await insertMessage(ctx)
  
  // Determine message type
  let messageType = 'unknown'
  let content = 'No text content'
  
  if (message.photo) {
    messageType = 'photo'
    content = `Photo: ${message.photo.length} sizes available`
  } else if (message.video) {
    messageType = 'video'
    content = `Video: ${message.video.file_name || 'No filename'}`
  } else if (message.document) {
    messageType = 'document'
    content = `Document: ${message.document.file_name || 'No filename'}`
  } else if (message.audio) {
    messageType = 'audio'
    content = `Audio: ${message.audio.file_name || 'No filename'}`
  } else if (message.voice) {
    messageType = 'voice'
    content = 'Voice message'
  } else if (message.sticker) {
    messageType = 'sticker'
    content = `Sticker: ${message.sticker.emoji || 'No emoji'}`
  } else if (message.animation) {
    messageType = 'animation'
    content = `Animation: ${message.animation.file_name || 'No filename'}`
  }
  
  // Create log entry for non-text messages
  const logEntry = {
    timestamp: new Date().toISOString(),
    chat_id: chat?.id,
    chat_type: chat?.type,
    chat_title: chat?.title || 'Unknown',
    user_id: from?.id,
    username: from?.username || 'Unknown',
    first_name: from?.first_name || 'Unknown',
    message_type: messageType,
    content: content,
    message_id: message.message_id,
    date: message.date ? convertUnixTimestamp(message.date) : new Date().toISOString()
  }
  
  // Log to console
  console.log('📨 New Message (Non-text):', JSON.stringify(logEntry, null, 2))
  
  // Only reply in private chats with debug information
  if (isPrivateChat(chat)) {
    const debugInfo = generateDebugInfo(ctx, logEntry)
    await ctx.reply(debugInfo)
  }
})

// Handle channel posts (when bot is admin in channel)
bot.on('channel_post', async (ctx) => {
  const post = ctx.channelPost
  const chat = ctx.chat
  
  // Store in database (no replies in channels)
  await upsertChat(chat)
  await insertMessage(ctx)
  
  const logEntry = {
    timestamp: new Date().toISOString(),
    chat_id: chat?.id,
    chat_type: 'channel',
    chat_title: chat?.title || 'Unknown',
    message_text: post.text || 'No text',
    message_id: post.message_id,
    date: post.date ? convertUnixTimestamp(post.date) : new Date().toISOString(),
    is_channel_post: true
  }
  
  console.log('📢 Channel Post:', JSON.stringify(logEntry, null, 2))
})

// Error handling
bot.catch((err) => {
  console.error('Bot error:', err)
})

const handleUpdate = webhookCallback(bot, 'std/http')

Deno.serve(async (req) => {
  try {
    const url = new URL(req.url)
    if (url.searchParams.get('secret') !== Deno.env.get('FUNCTION_SECRET')) {
      return new Response('not allowed', { status: 405 })
    }

    return await handleUpdate(req)
  } catch (err) {
    console.error(err)
  }
}) 