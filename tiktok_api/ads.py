class TikTokAdsAPI:
    @staticmethod
    def submit_ad(ad_payload, access_token):
        """Submit ad to TikTok Ads API (mocked)"""
        
        # Error 1: Invalid OAuth token
        if not access_token or access_token != "mock_access_token":
            return False, {
                "code": 401,
                "message": "Invalid or missing OAuth token. Please re-authenticate."
            }

        # Error 2: Missing permission scope
        # Simulating: Conversions objective requires special permission
        if ad_payload["objective"] == "Conversions":
            return False, {
                "code": 403,
                "message": "Missing 'ads:create:conversions' permission scope. Please update your TikTok app permissions."
            }

        # Error 3: Geo-restriction
        if ad_payload["campaign_name"].lower().startswith("india"):
            return False, {
                "code": 403,
                "message": "Geo-restriction: TikTok Ads are not available in this region."
            }

        # Error 4: Invalid music (additional check)
        if ad_payload["creative"]["music_id"] and not ad_payload["creative"]["music_id"].startswith("music_"):
            return False, {
                "code": 400,
                "message": "Invalid music_id format. Music ID must start with 'music_'."
            }

        # Success
        return True, {
            "ad_id": "ad_123456789",
            "status": "active",
            "created_at": "2024-02-04T10:30:00Z"
        }