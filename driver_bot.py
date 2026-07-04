from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from database import (
    init_db,
    create_order,
    save_order_message,
    update_order_status,
    get_active_orders,
    get_order
)

BOT_TOKEN = "8697634264:AAFnXcELinM2KjnFYwxuLU0zs23HwypEItI"
OWNER_ID = 583079615


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Բարև։\n\n"
        "Ուղարկեք պատվերի տվյալները.\n\n"
        "📌 Ինչ պետք է անել\n"
        "📍 Որտեղ պետք է անել\n"
        "🕒 Երբ պետք է անել\n"
        "⏳ Վերջնաժամկետը\n"
        "📷 Կարող եք կցել լուսանկարներ կամ ֆայլեր"
    )


async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id == OWNER_ID:
        return

    user = update.effective_user

    order_id = create_order(
        user.id,
        user.full_name,
        user.username
    )

    text = update.message.caption or update.message.text or ""

    save_order_message(
        order_id,
        "customer",
        "text",
        text
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Ընդունել",
                callback_data=f"accept:{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Մերժել",
                callback_data=f"decline:{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Լրացուցիչ տեղեկություն",
                callback_data=f"info:{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🎉 Ավարտել",
                callback_data=f"complete:{order_id}"
            )
        ]
    ])

    await update.message.forward(OWNER_ID)

    await context.bot.send_message(
        OWNER_ID,
        (
            f"📦 Նոր պատվեր #{order_id}\n"
            f"👤 {user.full_name}\n"
            f"📞 @{user.username if user.username else 'չկա'}"
        ),
        reply_markup=keyboard
    )

    await update.message.reply_text(
        "📨 Ձեր պատվերը հաջողությամբ ուղարկվել է։"
    )


async def active_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    orders = get_active_orders()

    if not orders:
        await update.message.reply_text(
            "📭 Ընթացիկ պատվերներ չկան։"
        )
        return

    text = "📋 Ընթացիկ պատվերներ\n\n"

    for order in orders:
        username = order["customer_username"]
        if username:
            username = f"@{username}"
        else:
            username = "չկա"

        text += (
            f"#{order['id']}\n"
            f"👤 {order['customer_name']}\n"
            f"📞 {username}\n"
            f"📅 {order['created_at']}\n\n"
        )

    await update.message.reply_text(text)


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    action, order_id = query.data.split(":")
    order_id = int(order_id)

    order = get_order(order_id)

    if not order:
        await query.message.reply_text(
            "❌ Պատվերը չի գտնվել։"
        )
        return

    customer_id = order["customer_id"]

    if action == "accept":
        update_order_status(order_id, "active")

        await context.bot.send_message(
            customer_id,
            "🔄 Ձեր պատվերն ընդունվել է և գտնվում է կատարման փուլում։"
        )

        await query.message.reply_text(
            f"✅ Պատվեր #{order_id}-ը ավելացվեց ընթացիկ պատվերների ցանկում։"
        )

    elif action == "decline":
        update_order_status(order_id, "declined")

        await context.bot.send_message(
            customer_id,
            "❌ Ձեր պատվերը մերժվել է։"
        )

    elif action == "info":
        await query.message.reply_text(
            "✏️ Այս ֆունկցիան կավելացվի հաջորդ տարբերակում։"
        )

    elif action == "complete":
        update_order_status(order_id, "completed")

        await context.bot.send_message(
            customer_id,
            "🎉 Ձեր պատվերը կատարվել է։"
        )

        await query.message.reply_text(
            f"✅ Պատվեր #{order_id}-ը ավարտված է։"
        )


def main():
    init_db()

    app = ApplicationBuilder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "active",
            active_orders
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callbacks
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            new_order
        )
    )

    print("Bot started")

    app.run_polling()


if __name__ == "__main__":
    main()
