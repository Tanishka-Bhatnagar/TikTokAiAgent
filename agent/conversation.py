from agent.state import AdState
from agent.rules import (
    validate_campaign_name,
    validate_objective,
    validate_ad_text,
    validate_cta
)
from tiktok_api.music import MusicAPI
from tiktok_api.ads import TikTokAdsAPI
from tiktok_api.oauth import OAuthService
import json

class ConversationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.state = AdState()
        self.oauth_service = OAuthService()

    def ask(self, user_input: str):
        step = self.state.current_step

        # ========== HANDLE COMPLETED STATE ==========
        if step == "complete":
            if user_input.lower() in ["restart", "start over", "new"]:
                self.state = AdState()  # Reset state
                return "Starting fresh! What's the campaign name?"
            return (
                "Conversation complete. Type 'restart' to create a new ad, or 'exit' to quit."
            )

        # ========== CAMPAIGN NAME ==========
        if step == "campaign_name":
            extracted = self._extract_with_llm(
                user_input, 
                "campaign_name",
                "Extract the campaign name from the user's message. Return only the name, nothing else."
            )
            
            valid, error = validate_campaign_name(extracted)
            if not valid:
                return error
            
            self.state.data["campaign_name"] = extracted
            self.state.current_step = "objective"
            return "Campaign name saved. What is the objective? (Traffic / Conversions)"

        # ========== OBJECTIVE ==========
        if step == "objective":
            extracted = self._extract_with_llm(
                user_input,
                "objective",
                """The user wants to set an ad objective. 
                Valid options: 'Traffic' or 'Conversions'
                
                User might say things like:
                - 'sales' → Conversions
                - 'traffic' → Traffic
                - 'clicks' → Traffic
                - 'purchases' → Conversions
                - 'i want sales' → Conversions
                
                Return ONLY 'Traffic' or 'Conversions'"""
            )
            
            valid, error = validate_objective(extracted)
            if not valid:
                return f"I understood '{extracted}', but objective must be exactly 'Traffic' or 'Conversions'. Please try again."
            
            self.state.data["objective"] = extracted
            self.state.current_step = "ad_text"
            return "Objective set. Please enter ad text (max 100 characters)."

        # ========== AD TEXT ==========
        if step == "ad_text":
            valid, error = validate_ad_text(user_input)
            if not valid:
                return error
            
            self.state.data["ad_text"] = user_input
            self.state.current_step = "cta"
            return "Ad text saved. What is the CTA?"

        # ========== CTA ==========
        if step == "cta":
            valid, error = validate_cta(user_input)
            if not valid:
                return error
            
            self.state.data["cta"] = user_input
            self.state.current_step = "music_choice"
            return (
                "Choose music option:\n"
                "1️⃣ Existing Music ID\n"
                "2️⃣ Upload Custom Music\n"
                "3️⃣ No Music"
            )

        # ========== MUSIC CHOICE ==========
        if step == "music_choice":
            choice = user_input.strip()
            
            # Case A: Existing Music ID
            if choice == "1":
                self.state.current_step = "music_id"
                return "Please enter the Music ID (must start with 'music_', e.g., music_1234)."

            # Case B: Upload Custom Music
            if choice == "2":
                print("\n[Simulating music upload...]")
                music_id = MusicAPI.upload_custom_music()
                print(f"[Generated Music ID: {music_id}]")
                
                valid, error = MusicAPI.validate_music_id(music_id)
                if not valid:
                    explanation = self._interpret_music_error(error)
                    return f"❌ Upload failed.\n\n{explanation}\n\nPlease choose another option (1, 2, or 3)."
                
                self.state.data["music_id"] = music_id
                self.state.current_step = "submit"
                return self._attempt_submission()

            # Case C: No Music
            if choice == "3":
                if self.state.data["objective"] == "Conversions":
                    return (
                        "❌ Music is REQUIRED for Conversion campaigns.\n"
                        "Please choose option 1 or 2."
                    )
                
                self.state.data["music_id"] = None
                self.state.current_step = "submit"
                return self._attempt_submission()

            return "Invalid choice. Please select 1, 2, or 3."

        # ========== MUSIC ID VALIDATION ==========
        if step == "music_id":
            # Check if user wants to go back
            if user_input.lower() == "back":
                self.state.current_step = "music_choice"
                return (
                    "Going back to music options.\n\n"
                    "Choose music option:\n"
                    "1️⃣ Existing Music ID\n"
                    "2️⃣ Upload Custom Music\n"
                    "3️⃣ No Music"
                )
            
            # Validate the music ID
            valid, error = MusicAPI.validate_music_id(user_input)
            if not valid:
                explanation = self._interpret_music_error(error)
                return (
                    f"❌ Music validation failed.\n\n{explanation}\n\n"
                    "You can:\n"
                    "- Enter a different Music ID (must start with 'music_')\n"
                    "- Type 'back' to choose another option"
                )
            
            self.state.data["music_id"] = user_input
            self.state.current_step = "submit"
            return self._attempt_submission()

        # ========== AFTER SUBMISSION ==========
        if step == "submit":
            if user_input.lower() == "retry":
                return self._attempt_submission()
            elif user_input.lower() == "restart":
                self.state = AdState()
                return "Starting fresh! What's the campaign name?"
            return (
                "Type 'retry' to attempt submission again, or 'restart' to create a new ad."
            )

        return "Conversation complete."

    # ========== LLM EXTRACTION ==========
    def _extract_with_llm(self, user_input: str, field_name: str, instruction: str):
        """Use LLM to extract structured data from user input"""
        prompt = f"""
{instruction}

User said: "{user_input}"

Return ONLY the extracted value, nothing else.
"""
        response = self.llm.generate(prompt)
        return response.strip()

    # ========== MUSIC ERROR INTERPRETATION ==========
    def _interpret_music_error(self, error: str):
        """Use LLM to explain music validation errors"""
        prompt = f"""
The TikTok Ads API rejected a music file with this error:
"{error}"

Explain to the user in simple, friendly terms:
1. What this error means
2. Why it might have happened
3. What they should do next

Keep it under 3 sentences.
"""
        return self.llm.generate(prompt)

    # ========== SUBMISSION ATTEMPT ==========
    def _attempt_submission(self):
        """Attempt to submit the ad and handle errors"""
        print("\n" + "="*50)
        print("ATTEMPTING SUBMISSION")
        print("="*50)
        print("\n[Step 1: OAuth Authorization...]")
        
        # Step 1: Get OAuth token
        token, oauth_error = self.oauth_service.authorize(
            "valid_client_id",
            "valid_client_secret"
        )
        
        if oauth_error:
            explanation = self._interpret_oauth_error(oauth_error)
            self.state.current_step = "submit"  # Allow retry
            return f"❌ Authorization failed.\n\n{explanation}\n\n(Type 'retry' to try again, or 'restart' for a new ad)"
        
        self.state.oauth["access_token"] = token
        print("  ✓ Access token obtained")
        
        # Step 2: Build payload
        payload = {
            "campaign_name": self.state.data["campaign_name"],
            "objective": self.state.data["objective"],
            "creative": {
                "text": self.state.data["ad_text"],
                "cta": self.state.data["cta"],
                "music_id": self.state.data["music_id"]
            }
        }
        
        print("\n[Step 2: Building Ad Payload...]")
        print(json.dumps(payload, indent=2))
        
        # Step 3: Submit ad
        print("\n[Step 3: Submitting to TikTok Ads API...]")
        success, result = TikTokAdsAPI.submit_ad(payload, token)
        
        if not success:
            explanation = self._interpret_api_error(result)
            print(f"  ✗ Submission failed - Code {result.get('code')}")
            self.state.current_step = "submit"  # Stay in submit state for retry
            return f"\n❌ SUBMISSION FAILED\n\n{explanation}\n\n(Type 'retry' to try again, or 'restart' for a new ad)"
        
        print("  ✓ Ad created successfully!")
        print("="*50)
        self.state.current_step = "complete"  # Mark as complete
        return f"\n✅ SUCCESS! Your ad has been created.\n\nAd ID: {result['ad_id']}\nStatus: {result.get('status', 'pending')}\n\n(Type 'restart' to create another ad, or 'exit' to quit)"

    # ========== API ERROR INTERPRETATION ==========
    def _interpret_api_error(self, error: dict):
        """Use LLM to explain API errors and suggest fixes"""
        prompt = f"""
The TikTok Ads API returned an error:
Code: {error.get('code')}
Message: {error.get('message')}

Explain to the user:
1. What went wrong in simple terms
2. What specifically they need to fix
3. Whether they can retry or need to start over

Be helpful and specific. Keep it under 4 sentences.
"""
        return self.llm.generate(prompt)

    def _interpret_oauth_error(self, error: str):
        """Use LLM to explain OAuth errors"""
        prompt = f"""
OAuth authorization failed with this error:
"{error}"

Explain to the user:
1. What this means
2. How to fix it (check credentials, scopes, etc.)

Keep it under 3 sentences.
"""
        return self.llm.generate(prompt)