"""
Configuration management for Azure Document Intelligence Demo
"""
import os
from typing import Optional


class Config:
    """Configuration class for Azure Document Intelligence settings"""

    def __init__(self):
        # Try Streamlit secrets first, then fall back to environment variables
        try:
            import streamlit as st
            self.azure_endpoint = st.secrets.get("azure", {}).get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv('AZURE_DI_ENDPOINT')
            self.azure_key = st.secrets.get("azure", {}).get("AZURE_DOCUMENT_INTELLIGENCE_KEY") or os.getenv('AZURE_DI_KEY')
        except (ImportError, FileNotFoundError, AttributeError):
            # Fall back to environment variables if Streamlit is not available or secrets not configured
            self.azure_endpoint = os.getenv('AZURE_DI_ENDPOINT')
            self.azure_key = os.getenv('AZURE_DI_KEY')

    def is_configured(self) -> bool:
        """Check if Azure credentials are properly configured"""
        return bool(self.azure_endpoint and self.azure_key)

    def get_missing_credentials(self) -> list:
        """Return list of missing environment variables"""
        missing = []
        if not self.azure_endpoint:
            missing.append('AZURE_DI_ENDPOINT')
        if not self.azure_key:
            missing.append('AZURE_DI_KEY')
        return missing

    @property
    def endpoint(self) -> Optional[str]:
        """Get Azure Document Intelligence endpoint"""
        return self.azure_endpoint

    @property
    def key(self) -> Optional[str]:
        """Get Azure Document Intelligence API key"""
        return self.azure_key


def get_config() -> Config:
    """Factory function to get configuration instance"""
    return Config()