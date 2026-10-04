import os
import html
import logging
import asyncio
import urllib.request
import xml.etree.ElementTree as ET

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# CONFIGURATION
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing.")

BOT_NAME = "SB24 LuckyGZ"

# Free RSS news sources
FOOTBALL_RSS = (
    "https://feeds.bbci.co.uk/sport/football/rss.xml"
)

SPORTS_RSS = (
    "https://feeds.bbci.co.uk/sport/rss.xml"
)

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# FETCH RSS NEWS
# =========================

def fetch_news(feed_url, limit=5):
    """
    Fetch news from a free RSS feed.
    No paid API key is required.
    """

    try:
        request = urllib.request.Request(
            feed_url,
            headers={
                "User-Agent": "Mozilla/5.0 SB24-LuckyGZ-NewsBot"
            },
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read()

        root = ET.fromstring(data)

        articles = []

        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            description = item.findtext("description", "")

            if title and link:
                # Remove HTML from description
                description = html.unescape(description)
                description = description.replace("<![CDATA[", "")
                description = description.replace("]]>", "")

                articles.append(
                    {
                        "title": title.strip(),
                        "link": link.strip(),
                        "description": description.strip(),
                    }
                )

        return articles

    except Exception as error:
        logger.error("RSS error: %s", error)
        return []


# =========================
# FORMAT NEWS
# =========================

def format_news(articles, category):
    if not articles:
        return (
            "⚠️ <b>News temporarily unavailable</b>\n\n"
            "Please try again in a few minutes."
        )

    message = f"📰 <b>{category}</b>\n\n"

    for index, article in enumerate(articles, start=1):

        title = html.escape(article["title"])

        # Keep descriptions short
        description = article["description"]

        if len(description) > 180:
            description = description[:180] + "..."

        description = html.escape(description)

        message += (
            f"<b>{index}. {title}</b>\n"
            f"{description}\n"
            f'<a href="{article["link"]}">Read full story</a>\n\n'
        )

    return message


# =========================
# MAIN MENU
# =========================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "⚽ Football News",
                callback_data="football"
            ),
            InlineKeyboardButton(
                "🏆 Sports News",
                callback_data="sports"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔄 Refresh News",
                callback_data="refresh"
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    first_name = html.escape(user.first_name or "there")

    message = (
        f"⚽ <b>Welcome to {BOT_NAME}!</b>\n\n"
        f"Hello {first_name} 👋\n\n"
        "Get the latest football and sports news, "
        "match updates, transfer news and team updates "
        "directly on Telegram.\n\n"
        "👇 Choose an option below:"
    )

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


# =========================
# FOOTBALL COMMAND
# =========================

async def football(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⏳ <b>Getting the latest football news...</b>",
        parse_mode=ParseMode.HTML,
    )

    articles = await asyncio.to_thread(
        fetch_news,
        FOOTBALL_RSS,
        5,
    )

    message = format_news(
        articles,
        "Latest Football News",
    )

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# =========================
# SPORTS COMMAND
# =========================

async def sports(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⏳ <b>Getting the latest sports news...</b>",
        parse_mode=ParseMode.HTML,
    )

    articles = await asyncio.to_thread(
        fetch_news,
        SPORTS_RSS,
        5,
    )

    message = format_news(
        articles,
        "Latest Sports News",
    )

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "football":

        await query.edit_message_text(
            "⏳ <b>Getting the latest football news...</b>",
            parse_mode=ParseMode.HTML,
        )

        articles = await asyncio.to_thread(
            fetch_news,
            FOOTBALL_RSS,
            5,
        )

        message = format_news(
            articles,
            "Latest Football News",
        )

        await query.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    elif query.data == "sports":

        await query.edit_message_text(
            "⏳ <b>Getting the latest sports news...</b>",
            parse_mode=ParseMode.HTML,
        )

        articles = await asyncio.to_thread(
            fetch_news,
            SPORTS_RSS,
            5,
        )

        message = format_news(
            articles,
            "Latest Sports News",
        )

        await query.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    elif query.data == "refresh":

        await query.edit_message_text(
            "🔄 <b>Refreshing the news...</b>",
            parse_mode=ParseMode.HTML,
        )

        articles = await asyncio.to_thread(
            fetch_news,
            FOOTBALL_RSS,
            5,
        )

        message = format_news(
            articles,
            "Latest Football News",
        )

        await query.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu(),
            disable_web_page_preview=True,
        )


# =========================
# HELP COMMAND
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = (
        "ℹ️ <b>SB24 LuckyGZ</b>\n\n"
        "Your sports news assistant on Telegram.\n\n"
        "<b>Available commands:</b>\n"
        "/start - Open the main menu\n"
        "/football - Latest football news\n"
        "/sports - Latest sports news\n"
        "/help - Show help"
    )

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu(),
    )


# =========================
# ERROR HANDLER
# =========================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "Exception while handling update:",
        exc_info=context.error,
    )


# =========================
# START BOT
# =========================

def main():

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("football", football)
    )

    application.add_handler(
        CommandHandler("sports", sports)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    # Buttons
    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # Errors
    application.add_error_handler(error_handler)

    logger.info("%s is running...", BOT_NAME)

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
