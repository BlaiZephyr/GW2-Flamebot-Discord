import discord
from discord.ext import commands
import asyncio
import os
import sys
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    print(f'Ready to receive commands!')

@bot.command(name='flame')
async def send_report(ctx, *urls_or_file):
    """Generate and send GW2 raid flame from URL(s) or input file"""
    initial_msg = await ctx.send("Generating flame... This may take a moment.")
    
    process = None
    temp_input = None
    thread = None
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If no arguments, use default input.txt
        if not urls_or_file:
            urls_or_file = ('input.txt',)
        
        # Check if first argument is a URL or file
        first_arg = urls_or_file[0]
        if first_arg.startswith('http://') or first_arg.startswith('https://'):
            # Create temp file with all URLs
            temp_input = os.path.join(script_dir, 'temp_input.txt')
            
            # Collect all URLs from the original message content
            message_content = ctx.message.content
            
            # Debug: print the raw message
            print(f"Raw message content: {message_content}")
            print(f"Parsed args count: {len(urls_or_file)}")
            print(f"Parsed args: {urls_or_file}")
            
            # Remove the command part
            message_without_command = message_content.split(maxsplit=1)
            
            all_urls = []
            if len(message_without_command) > 1:
                # Improved URL extraction - handles Discord formatting better
                url_text = message_without_command[1]
                
                # Remove Discord's <> wrapping
                url_text = url_text.replace('<', '').replace('>', '')
                
                # Extract all URLs using regex
                found_urls = re.findall(r'https?://[^\s]+', url_text)
                
                # Clean each URL more thoroughly
                for url in found_urls:
                    # Remove trailing punctuation and markdown
                    cleaned = re.sub(r'[_*\)\],\.]+$', '', url)
                    # Remove any remaining special characters at the end
                    cleaned = cleaned.rstrip('_*<>[](),.;!')
                    if cleaned:
                        all_urls.append(cleaned)
            
            # Fallback to parsed arguments if regex didn't find anything
            if not all_urls:
                all_urls = []
                for url in urls_or_file:
                    # Clean URLs from parsed arguments too
                    cleaned = url.replace('<', '').replace('>', '').strip()
                    cleaned = cleaned.rstrip('_*<>[](),.;!')
                    if cleaned:
                        all_urls.append(cleaned)
            
            if not all_urls:
                await initial_msg.edit(content="No valid URLs found!")
                return
            
            # Write to temp file
            with open(temp_input, 'w') as f:
                for url in all_urls:
                    f.write(url + '\n')
            
            # Print temp file contents for debugging
            print(f"\nTemp file contents ({temp_input}):")
            with open(temp_input, 'r') as f:
                print(f.read())
            
            input_file = 'temp_input.txt'
            await initial_msg.edit(content=f"Processing {len(all_urls)} URL(s)...")
            
            # Debug: log what URLs were captured
            print(f"\nCaptured {len(all_urls)} URLs:")
            for i, url in enumerate(all_urls, 1):
                print(f"  {i}. {url}")
        else:
            # Treat as filename
            input_file = first_arg
        
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            'main.py',
            '-i', input_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=script_dir
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
            await initial_msg.edit(content=f"Error running report:\n```\n{error_msg[:1000]}\n```")
            return
        
        # Read the output file
        output_file = os.path.join(script_dir, "Flame_Output.txt")
        if not os.path.exists(output_file):
            await initial_msg.edit(content="Report file not found! Make sure main.py ran successfully.")
            return
        
        with open(output_file, "r", encoding="utf-8") as f:
            report_text = f.read()
        
        if not report_text.strip():
            await initial_msg.edit(content="dps.report reports as empty, Check your input file.")
            return
        
        # Create a thread for the report
        thread_name = "Flame Report"
        if first_arg.startswith('http'):
            # Try to extract boss/encounter name from report if possible
            first_line = report_text.split('\n')[0] if report_text else ""
            if first_line and len(first_line) < 100:
                thread_name = f"{first_line[:80]}"
        
        # Create thread from the initial message
        thread = await initial_msg.create_thread(
            name=thread_name,
            auto_archive_duration=1440  # 24 hours
        )
        
        await initial_msg.edit(content=f"flame generated")
        
        # Send report in the thread
        if len(report_text) <= 1990:
            await thread.send(report_text)
        else:
            # Split into chunks of 1900 chars (leaving room for formatting)
            await thread.send("flame generated. Sending in multiple parts:")
            chunks = []
            current_chunk = ""
            
            for line in report_text.split('\n'):
                if len(current_chunk) + len(line) + 1 > 1900:
                    chunks.append(current_chunk)
                    current_chunk = line + '\n'
                else:
                    current_chunk += line + '\n'
            
            if current_chunk:
                chunks.append(current_chunk)
            
            for i, chunk in enumerate(chunks, 1):
                await thread.send(f"{chunk}")
                if i < len(chunks):
                    await asyncio.sleep(0.5)
    
    except asyncio.TimeoutError:
        await initial_msg.edit(content="flame generation timed out (took longer than 2 minutes)")
        if process:
            try:
                process.kill()
                await process.wait()
            except:
                pass
    
    except FileNotFoundError as e:
        if 'main.py' in str(e):
            await initial_msg.edit(content=f"main.py script not found in {script_dir}")
        else:
            await initial_msg.edit(content=f"Input file not found!")
    
    except Exception as e:
        error_content = f"Error generating report: {str(e)}"
        if thread:
            await thread.send(error_content)
        else:
            await initial_msg.edit(content=error_content)
        print(f"Full error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup temp file if it was created
        if temp_input and os.path.exists(temp_input):
            try:
                os.remove(temp_input)
            except:
                pass

@bot.command(name='ping')
async def ping(ctx):
    """Check if bot is responsive"""
    await ctx.send(f'shut the fuck up! Latency: {round(bot.latency * 1000)}ms')

if __name__ == "__main__":
    print("Starting GW2 Flamebot Discord bot...")
    print("Press Ctrl+C to stop")
    try:
        bot.run(os.environ.get('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")