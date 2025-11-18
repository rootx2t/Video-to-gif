import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import moviepy.editor as mp
import tempfile
from io import BytesIO

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VideoToGifBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.VIDEO_NOTE, self.handle_video_note))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when the command /start is issued."""
        await update.message.reply_text(
            "🎬 Welcome to Video to GIF Bot!\n\n"
            "Just send me a video and I'll convert it to a GIF for you!\n\n"
            "Commands:\n"
            "/start - Show this welcome message\n"
            "/help - Get help information"
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when the command /help is issued."""
        await update.message.reply_text(
            "🤖 How to use this bot:\n\n"
            "1. Send me any video file (max 20MB)\n"
            "2. I'll convert it to a GIF\n"
            "3. You'll receive the GIF back\n\n"
            "Supported formats: MP4, MOV, AVI, and other common video formats\n\n"
            "Note: Very long videos will be trimmed to the first 10 seconds."
        )
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert video to GIF."""
        try:
            video = update.message.video
            
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Processing your video...")
            
            # Download video
            video_file = await video.get_file()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                await video_file.download_to_drive(temp_video.name)
                
                # Convert to GIF
                gif_path = await self.convert_video_to_gif(temp_video.name)
                
                # Clean up temp video file
                os.unlink(temp_video.name)
            
            if gif_path:
                # Send the GIF
                with open(gif_path, 'rb') as gif_file:
                    await update.message.reply_animation(
                        animation=gif_file,
                        caption="Here's your GIF! 🎉"
                    )
                
                # Clean up temp GIF file
                os.unlink(gif_path)
                await processing_msg.delete()
            else:
                await update.message.reply_text("❌ Failed to convert video to GIF.")
                
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            await update.message.reply_text("❌ An error occurred while processing your video.")
    
    async def handle_video_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Convert video note (round video) to GIF."""
        try:
            video_note = update.message.video_note
            
            # Send processing message
            processing_msg = await update.message.reply_text("🔄 Processing your video note...")
            
            # Download video note
            video_file = await video_note.get_file()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                await video_file.download_to_drive(temp_video.name)
                
                # Convert to GIF
                gif_path = await self.convert_video_to_gif(temp_video.name)
                
                # Clean up temp video file
                os.unlink(temp_video.name)
            
            if gif_path:
                # Send the GIF
                with open(gif_path, 'rb') as gif_file:
                    await update.message.reply_animation(
                        animation=gif_file,
                        caption="Here's your GIF from video note! 🎉"
                    )
                
                # Clean up temp GIF file
                os.unlink(gif_path)
                await processing_msg.delete()
            else:
                await update.message.reply_text("❌ Failed to convert video note to GIF.")
                
        except Exception as e:
            logger.error(f"Error processing video note: {e}")
            await update.message.reply_text("❌ An error occurred while processing your video note.")
    
    async def convert_video_to_gif(self, video_path, max_duration=10):
        """Convert video file to GIF with moviepy."""
        try:
            # Load video
            video = mp.VideoFileClip(video_path)
            
            # Trim if too long
            if video.duration > max_duration:
                video = video.subclip(0, max_duration)
            
            # Create temp file for GIF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as temp_gif:
                gif_path = temp_gif.name
            
            # Convert to GIF with optimized settings
            video.write_gif(
                gif_path,
                fps=10,  # Lower FPS for smaller file size
                program='ffmpeg',
                opt='OptimizePlus'
            )
            
            video.close()
            return gif_path
            
        except Exception as e:
            logger.error(f"Error in video conversion: {e}")
            return None
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors."""
        logger.error(f"Exception while handling an update: {context.error}")
    
    def run(self):
        """Start the bot."""
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Get bot token from environment variable
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable is not set!")
        exit(1)
    
    bot = VideoToGifBot(BOT_TOKEN)
    print("Bot is running...")
    bot.run()