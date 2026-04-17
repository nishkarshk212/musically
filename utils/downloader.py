"""
YouTube/Audio Downloader using NexGen API
Handles downloading and extracting metadata
"""

import os
import yt_dlp
import asyncio
import aiohttp
from typing import Optional, Dict
from config import DOWNLOAD_DIR, MAX_DURATION
import logging

logger = logging.getLogger(__name__)

# NexGen API configuration
NEXGEN_API_URL = os.getenv("NEXGENBOTS_API", "https://pvtz.nexgenbots.xyz")
API_KEY = os.getenv("API_KEY")


class SongInfo:
    """Container for song information"""
    
    def __init__(self):
        self.title: str = ""
        self.duration: int = 0  # in seconds
        self.thumbnail: str = ""
        self.channel: str = ""
        self.video_id: str = ""
        self.url: str = ""
        self.file_path: str = ""


class Downloader:
    """Handles downloading audio from various sources using NexGen API"""
    
    def __init__(self):
        self.download_dir = DOWNLOAD_DIR
        os.makedirs(self.download_dir, exist_ok=True)
    
    def get_ydl_opts(self, output_path: str) -> Dict:
        """Get yt-dlp options"""
        return {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'geo_bypass': True,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'prefer_ffmpeg': True,
            'ffmpeg_location': '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew default
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    
    async def extract_info(self, url: str) -> Optional[SongInfo]:
        """Extract information from URL using NexGen API"""
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                return None
            
            # FASTEST: Use yt-dlp metadata extraction without full download
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Fast extraction
                'skip_download': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'socket_timeout': 5,
            }
            
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            
            if not info:
                return None
            
            song = SongInfo()
            song.title = info.get('title', 'Unknown')
            song.duration = int(info.get('duration', 0))
            song.thumbnail = info.get('thumbnail', '')
            song.channel = info.get('uploader', 'Unknown')
            song.video_id = video_id
            song.url = url
            
            return song
            
        except Exception as e:
            logger.error(f"Failed to extract info: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        if "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0]
        return url
    
    async def download_song(self, url: str, song_info: SongInfo) -> Optional[str]:
        """
        Download song using NexGen API
        
        Args:
            url: Video URL
            song_info: Song information
            
        Returns:
            Path to downloaded file or None
        """
        try:
            # Check duration limit
            if song_info.duration > MAX_DURATION:
                logger.error(f"Song too long: {song_info.duration}s")
                return None
            
            video_id = song_info.video_id
            # Use m4a format for better compatibility with PyTgCalls
            file_path = os.path.join(self.download_dir, f"{video_id}.m4a")
            
            # Check if already downloaded
            if os.path.exists(file_path):
                logger.info(f"✅ [NEXGEN] File already exists: {file_path}")
                song_info.file_path = file_path
                return file_path
            
            # Use NexGen API to download
            logger.info(f"🎵 [NEXGEN] Using API: {NEXGEN_API_URL}/song/{video_id}")
            
            async with aiohttp.ClientSession() as session:
                # Step 1: Get the stream URL
                api_url = f"{NEXGEN_API_URL}/song/{video_id}"
                params = {"api": API_KEY} if API_KEY else {}
                
                async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            status = data.get("status")
                            stream_link = data.get("link")
                            
                            if status == "done" and stream_link:
                                logger.info(f"✅ [NEXGEN] Got stream link, downloading...")
                                
                                # Step 2: Download from the stream URL with better error handling
                                logger.info(f"📥 [NEXGEN] Downloading from: {stream_link}")
                                async with session.get(stream_link, timeout=aiohttp.ClientTimeout(total=300)) as stream_response:
                                    if stream_response.status == 200:
                                        # Download with proper chunk handling to prevent corruption
                                        with open(file_path, 'wb') as f:
                                            async for chunk in stream_response.content.iter_chunked(32768):  # Larger chunks for stability
                                                f.write(chunk)
                                        
                                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                            logger.info(f"✅ [NEXGEN] Successfully downloaded: {file_path}")
                                            song_info.file_path = file_path
                                            return file_path
                                        else:
                                            logger.error(f"❌ [NEXGEN] File empty or corrupted")
                                            return None
                                    else:
                                        logger.error(f"❌ [NEXGEN] Stream download failed: {stream_response.status}")
                                        return None
                            elif status == "downloading":
                                logger.info("⏳ [NEXGEN] Still processing, waiting...")
                                await asyncio.sleep(5)
                                # Retry once
                                return await self.download_song(url, song_info)
                            else:
                                logger.warning(f"⚠️ [NEXGEN] Unexpected status: {status}")
                                return None
                        else:
                            logger.warning(f"⚠️ [NEXGEN] Empty response")
                            return None
                    else:
                        logger.warning(f"⚠️ [NEXGEN] API returned status {response.status}")
                        return None
                
        except Exception as e:
            logger.error(f"❌ [NEXGEN] Failed to download song: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def search_and_download(self, query: str) -> Optional[SongInfo]:
        """Search for a song and download it using yt-dlp search + NexGen API download"""
        try:
            # Search on YouTube using yt-dlp - ULTRA FAST options
            search_url = f"ytsearch1:{query}"
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # FAST: don't extract metadata of entries
                'skip_download': True,
                'playlist_items': '1',
                'nocheckcertificate': True,
                'socket_timeout': 5,
            }
            
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(search_url, download=False))
            
            if not info or 'entries' not in info or not info['entries']:
                return None
            
            video_info = info['entries'][0]
            video_id = video_info.get('id')
            if not video_id:
                return None
                
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Create SongInfo directly from search result (FASTEST)
            song_info = SongInfo()
            song_info.title = video_info.get('title', 'Unknown')
            song_info.duration = int(video_info.get('duration', 0))
            song_info.thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            song_info.channel = video_info.get('uploader', 'Unknown')
            song_info.views = video_info.get('view_count', '0')
            song_info.video_id = video_id
            song_info.url = video_url
            
            # Download using NexGen API (non-blocking)
            file_path = await self.download_song(video_url, song_info)
            if file_path:
                return song_info
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to search and download: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def cleanup_file(self, file_path: str):
        """Delete downloaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file: {e}")
    
    async def download_thumbnail(self, thumbnail_url: str, output_path: str) -> Optional[str]:
        """
        Download thumbnail from URL
        
        Args:
            thumbnail_url: URL of the thumbnail
            output_path: Path to save the thumbnail
            
        Returns:
            Path to downloaded thumbnail or None
        """
        try:
            if not thumbnail_url:
                return None
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                            logger.info(f"✅ Downloaded thumbnail: {output_path}")
                            return output_path
                        else:
                            logger.error(f"❌ Thumbnail file is empty")
                            return None
                    else:
                        logger.error(f"❌ Failed to download thumbnail: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"❌ Failed to download thumbnail: {e}")
            return None
    
    def cleanup_all(self):
        """Clean up all downloaded files"""
        try:
            for filename in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            logger.info("Cleaned up all downloads")
        except Exception as e:
            logger.error(f"Failed to cleanup all: {e}")


# Global downloader instance
downloader = Downloader()
