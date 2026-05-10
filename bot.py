import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from config import settings, load_active_model, save_active_model
from utils import format_response_time, is_admin, truncate_text
from generate_reply import generate_reply
from model_fetcher import get_all_providers_models
from exceptions import MissingAPIKeyError, ModelAPIError
from model_stats import increment_stat, format_stats_message, get_stats

MODELS_PER_PAGE = 8

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    welcome_text = (
        f"નમસ્તે! હું {settings.BUSINESS_NAME} નો AI આસિસ્ટન્ટ છું. "
        "તમે મને દુકાન, પ્રોડક્ટ્સ, અથવા સેવાઓ વિશે કોઈ પણ પ્રશ્ન પૂછી શકો છો."
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    help_text = (
        "હું તમને નીચેની માહિતી આપી શકું છું:\n"
        "- દુકાન નો સમય અને સરનામું\n"
        "- પ્રોડક્ટ્સ અને સેવાઓ ની વિગત\n"
        "- આજનો સોના/ચાંદી નો ભાવ (જો ઉપલબ્ધ હોય તો)\n"
        "- કોઈ પણ અન્ય સામાન્ય પ્રશ્નો\n\n"
        "ફક્ત તમારો પ્રશ્ન ગુજરાતી માં લખીને મોકલો."
    )
    await update.message.reply_text(help_text)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all normal text messages."""
    user_id = str(update.message.from_user.id)
    message_text = update.message.text

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    try:
        active = load_active_model()
        provider = active["provider"]
        model = active["model"]

        reply = await generate_reply(
            message=message_text,
            business_id=settings.BUSINESS_ID,
            user_id=user_id
        )

        # Track successful reply
        increment_stat(provider, model)

        await update.message.reply_text(reply)

    except MissingAPIKeyError as e:
        logging.error(str(e))
        error_msg = "માફ કરશો, સિસ્ટમ માં ક્ષતિ છે. (API Key Missing)"
        await update.message.reply_text(error_msg)

        # Notify admin in English
        if settings.ADMIN_TELEGRAM_ID:
            try:
                await context.bot.send_message(
                    chat_id=settings.ADMIN_TELEGRAM_ID,
                    text=f"🚨 ERROR: {str(e)}"
                )
            except Exception as admin_err:
                logging.error(f"Could not notify admin: {admin_err}")

    except ModelAPIError as e:
        logging.error(str(e))
        await update.message.reply_text("માફ કરશો, હમણાં technical problem છે. કૃપા કરીને થોડી વાર પછી પ્રયાસ કરો.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await update.message.reply_text("માફ કરશો, સિસ્ટમ માં ક્ષતિ છે.")

async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles non-text messages (images, audio, etc)."""
    await update.message.reply_text("હું ફક્ત text message સમજી શકું છું.")

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown /commands."""
    await update.message.reply_text("આ command મને સમજાઈ નહીં. /help લખો મદદ માટે.")

# --- ADMIN COMMANDS ---

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the current active model."""
    if not is_admin(update.message.from_user.id):
        return

    active = load_active_model()
    text = (
        "Current Model:\n"
        f"Provider: {active['provider'].capitalize()}\n"
        f"Model: {active['model']}\n"
    )
    await update.message.reply_text(text)

async def testmodel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tests the active model's speed and response."""
    if not is_admin(update.message.from_user.id):
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    start_time = time.time()
    test_message = "તમારી દુકાન વિશે જણાવો"

    try:
        reply = await generate_reply(
            message=test_message,
            business_id=settings.BUSINESS_ID,
            user_id="admin_test"
        )
        end_time = time.time()

        ms_diff = (end_time - start_time) * 1000
        time_str = format_response_time(ms_diff)

        await update.message.reply_text(f"Response ({time_str}):\n\n{reply}")
    except Exception as e:
        await update.message.reply_text(f"Test failed: {e}")

async def modelstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows model usage stats."""
    if not is_admin(update.message.from_user.id):
        return

    stats_msg = format_stats_message()
    await update.message.reply_text(stats_msg)

async def listmodels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists all available models by checking APIs or config."""
    if not is_admin(update.message.from_user.id):
        return

    await update.message.reply_text("Fetching live model list... This may take a few seconds.")

    all_models = await get_all_providers_models()

    text_lines = ["Available Models:\n"]
    for provider, models in all_models.items():
        if not models:
            continue
        text_lines.append(f"== {provider.upper()} ==")
        for m in models:
            text_lines.append(f"- {m['label']} ({m['id']})")
        text_lines.append("")

    # Cap message size if too big
    full_text = "\n".join(text_lines)
    if len(full_text) > 4000:
        full_text = full_text[:4000] + "\n... (truncated)"

    await update.message.reply_text(full_text)

# --- SWITCHMODEL FLOW ---

def build_provider_keyboard() -> InlineKeyboardMarkup:
    """Builds the initial keyboard to select a provider."""
    keyboard = [
        [
            InlineKeyboardButton("Anthropic Claude", callback_data="provider:anthropic"),
            InlineKeyboardButton("OpenAI", callback_data="provider:openai")
        ],
        [
            InlineKeyboardButton("Google Gemini", callback_data="provider:google"),
            InlineKeyboardButton("OpenRouter", callback_data="provider:openrouter")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_model_keyboard(models: list, provider: str, page: int = 0) -> InlineKeyboardMarkup:
    """Builds the paginated keyboard for selecting a model."""
    start = page * MODELS_PER_PAGE
    end = start + MODELS_PER_PAGE
    page_models = models[start:end]
    total_pages = (len(models) + MODELS_PER_PAGE - 1) // MODELS_PER_PAGE

    if total_pages == 0:
        total_pages = 1

    buttons = []

    # Model buttons in pairs
    for i in range(0, len(page_models), 2):
        row = [
            InlineKeyboardButton(
                truncate_text(page_models[i]["label"], 30),
                callback_data=f"model:{provider}:{page_models[i]['id']}"
            )
        ]
        if i + 1 < len(page_models):
            row.append(
                InlineKeyboardButton(
                    truncate_text(page_models[i+1]["label"], 30),
                    callback_data=f"model:{provider}:{page_models[i+1]['id']}"
                )
            )
        buttons.append(row)

    # Navigation row
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀ Prev", callback_data=f"page:{provider}:{page-1}"))

    nav_row.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))

    if end < len(models):
        nav_row.append(InlineKeyboardButton("Next ▶", callback_data=f"page:{provider}:{page+1}"))

    if nav_row:
        buttons.append(nav_row)

    # Back button always at bottom
    buttons.append([InlineKeyboardButton("🔙 Back to Providers", callback_data="back:providers")])

    return InlineKeyboardMarkup(buttons)

async def switchmodel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the model switching flow."""
    if not is_admin(update.message.from_user.id):
        return

    await update.message.reply_text(
        "Select an AI Provider:",
        reply_markup=build_provider_keyboard()
    )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    data = query.data

    if data == "noop":
        return

    elif data == "back:providers":
        await query.edit_message_text(
            "Select an AI Provider:",
            reply_markup=build_provider_keyboard()
        )

    elif data.startswith("provider:"):
        provider = data.split(":")[1]

        # Give immediate feedback that we're loading
        await query.edit_message_text(f"Fetching models for {provider.capitalize()}...")

        all_models = await get_all_providers_models()
        models = all_models.get(provider, [])

        if not models:
            await query.edit_message_text(
                f"No models found for {provider.capitalize()} (missing API key?).",
                reply_markup=build_provider_keyboard()
            )
            return

        await query.edit_message_text(
            f"Select a model for {provider.capitalize()}:",
            reply_markup=build_model_keyboard(models, provider, page=0)
        )

    elif data.startswith("page:"):
        parts = data.split(":")
        provider = parts[1]
        page = int(parts[2])

        all_models = await get_all_providers_models()
        models = all_models.get(provider, [])

        await query.edit_message_reply_markup(
            reply_markup=build_model_keyboard(models, provider, page=page)
        )

    elif data.startswith("model:"):
        parts = data.split(":")
        provider = parts[1]
        model_id = ":".join(parts[2:]) # In case model ID has colons

        save_active_model(provider, model_id, changed_by=query.from_user.id)

        await query.edit_message_text(
            f"✅ Model changed to {model_id}\n"
            f"Provider: {provider.capitalize()}\n"
            "All new messages will use this model."
        )

def get_bot_application() -> Application:
    """Creates and configures the bot application."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logging.warning("TELEGRAM_BOT_TOKEN is not set. Bot will fail to start.")

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN or "DUMMY").build()

    # Standard commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Admin commands
    app.add_handler(CommandHandler("model", model_command))
    app.add_handler(CommandHandler("switchmodel", switchmodel_command))
    app.add_handler(CommandHandler("testmodel", testmodel_command))
    app.add_handler(CommandHandler("listmodels", listmodels_command))
    app.add_handler(CommandHandler("modelstats", modelstats_command))
    app.add_handler(CommandHandler("refreshmodels", listmodels_command)) # Alias

    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command)) # Catch-all for unknown commands
    app.add_handler(MessageHandler(~filters.TEXT & ~filters.COMMAND, handle_non_text))

    return app
