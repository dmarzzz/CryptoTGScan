// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

console.log(`Function "telegram-bot" up and running!`)

import { Bot, webhookCallback } from 'https://deno.land/x/grammy@v1.8.3/mod.ts'

const bot = new Bot(Deno.env.get('TELEGRAM_BOT_TOKEN') || '')

// Bot commands
bot.command('start', (ctx) => ctx.reply('Welcome! Up and running.'))

bot.command('ping', (ctx) => ctx.reply(`Pong! ${new Date()} ${Date.now()}`))

// Helper function to convert Unix timestamp to ISO string
function convertUnixTimestamp(timestamp: number): string {
  return new Date(timestamp * 1000).toISOString()
}

// Handle all text messages from channels and groups
bot.on('message:text', async (ctx) => {
  const message = ctx.message
  const chat = ctx.chat
  const from = ctx.from
  
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
  
  // Optional: Send confirmation for debugging
  if (chat?.type === 'private') {
    await ctx.reply('✅ Message logged!')
  }
})

// Handle all non-text messages (photos, videos, documents, etc.)
bot.on('message', async (ctx) => {
  const message = ctx.message
  const chat = ctx.chat
  const from = ctx.from
  
  // Skip if it's a text message (already handled above)
  if (message.text) return
  
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
  
  // Optional: Send confirmation for debugging
  if (chat?.type === 'private') {
    await ctx.reply(`✅ ${messageType} message logged!`)
  }
})

// Handle channel posts (when bot is admin in channel)
bot.on('channel_post', async (ctx) => {
  const post = ctx.channelPost
  const chat = ctx.chat
  
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