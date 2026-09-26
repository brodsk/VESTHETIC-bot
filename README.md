# VESTHETIC Bot — GitHub + Vercel

Deploy this repository as a Vercel Python Function.

Environment variables in Vercel:
- BOT_TOKEN
- ADMIN_IDS
- MANAGER_USERNAME

After deployment set the Telegram webhook:
`https://api.telegram.org/botYOUR_TOKEN/setWebhook?url=https://YOUR-VERCEL-DOMAIN/api/webhook`

Check it with `getWebhookInfo`.

This is an MVP. Conversation state is in function memory, so the next production step is Supabase/Postgres persistence.
