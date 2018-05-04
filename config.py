# config.py

class chromaTuneConfig:
    def __init__(self):
        self.plotly_username = ''
        self.plotly_api_key = ''

        self.spotify_client_id = ''
        self.spotify_client_secret = ''

    def plotly_credentials(self):
        """Returns user and API key"""
        return (self.plotly_username,self.plotly_api_key)

    def spotify_credentials(self):
        """Returns API client ID and client secret"""
        return (self.spotify_client_id, self.spotify_client_secret)