import random

class MusicAPI:
    @staticmethod
    def validate_music_id(music_id: str):
        """Validate music ID against TikTok's music library (mocked)"""
        
        # Valid format check
        if not music_id.startswith("music_"):
            return False, "Music ID must start with 'music_'. Example: music_1234"
        
        # Simulate random failures
        if random.random() < 0.3:  # 30% failure rate
            errors = [
                "Music not found in TikTok library",
                "Music copyright restricted in target region",
                "Music removed due to policy violation",
                "Music requires additional licensing"
            ]
            return False, random.choice(errors)
        
        return True, None

    @staticmethod
    def upload_custom_music():
        """Simulate uploading custom music and generating ID"""
        music_id = f"music_{random.randint(1000, 9999)}"
        print(f"  → Uploading music...")
        print(f"  → Generated ID: {music_id}")
        return music_id