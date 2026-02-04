class AdState:
    def __init__(self):
        self.data = {
            "campaign_name": None,
            "objective": None,
            "ad_text": None,
            "cta": None,
            "music_id": None
        }
        self.oauth = {
            "access_token": None
        }
        self.current_step = "campaign_name"  # Possible values: campaign_name, objective, ad_text, cta, music_choice, music_id, submit, complete

    def is_complete(self):
        """Check if all required fields are filled"""
        return all([
            self.data["campaign_name"],
            self.data["objective"],
            self.data["ad_text"],
            self.data["cta"]
        ])