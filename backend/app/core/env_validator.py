"""
Environment Variables Validation Script

Validates that all required environment variables are set
before the application starts. This prevents cryptic errors
at runtime due to missing configuration.

Run this script before starting the application:
    python -m app.core.env_validator

Or import and call validate_environment() in your startup code.
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class EnvironmentValidator:
    """Validates required environment variables"""
    
    # Define required variables with descriptions
    REQUIRED_VARS = {
        # API Keys (Critical)
        "ANTHROPIC_API_KEY": {
            "description": "Anthropic Claude API key",
            "example": "sk-ant-xxxxx",
            "critical": True
        },
        "OPENAI_API_KEY": {
            "description": "OpenAI API key for embeddings",
            "example": "sk-xxxxx",
            "critical": True
        },
        "PINECONE_API_KEY": {
            "description": "Pinecone vector database API key",
            "example": "pcsk-xxxxx",
            "critical": True
        },
        
        # Database
        "DATABASE_URL": {
            "description": "PostgreSQL connection string",
            "example": "postgresql://user:pass@localhost:5432/dbname",
            "critical": True
        },
        "REDIS_URL": {
            "description": "Redis connection string",
            "example": "redis://localhost:6379",
            "critical": True
        },
        
        # Pinecone Configuration
        "PINECONE_INDEX_NAME": {
            "description": "Name of the Pinecone index",
            "example": "chatbot-pdfs",
            "critical": True
        },
        
        # Application Configuration
        "ENVIRONMENT": {
            "description": "Environment name",
            "example": "development, production",
            "critical": False,
            "default": "development"
        },
        "LOG_LEVEL": {
            "description": "Logging level",
            "example": "INFO, DEBUG, WARNING, ERROR",
            "critical": False,
            "default": "INFO"
        }
    }
    
    # Optional but recommended variables
    OPTIONAL_VARS = {
        "SECRET_KEY": "Secret key for sessions",
        "ALLOWED_ORIGINS": "CORS allowed origins",
        "LLM_MODEL": "LLM model to use",
        "TEMPERATURE": "LLM temperature",
        "MAX_TOKENS": "Max tokens per response",
        "EMBEDDING_MODEL": "Embedding model",
        "TOP_K": "Number of results to retrieve"
    }
    
    def __init__(self, strict: bool = True):
        """
        Args:
            strict: If True, exit on missing critical variables
        """
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.valid = True
    
    def validate(self) -> bool:
        """
        Validate all required environment variables
        
        Returns:
            bool: True if all critical variables are set, False otherwise
        """
        print("\n" + "="*60)
        print("🔍 VALIDATING ENVIRONMENT VARIABLES")
        print("="*60 + "\n")
        
        # Check required variables
        for var_name, var_info in self.REQUIRED_VARS.items():
            self._check_variable(var_name, var_info)
        
        # Check optional variables
        print("\n📋 Optional Variables:")
        for var_name, description in self.OPTIONAL_VARS.items():
            value = os.getenv(var_name)
            if value:
                print(f"  ✅ {var_name}: Set")
            else:
                print(f"  ⚠️  {var_name}: Not set (using default)")
                self.warnings.append(f"{var_name} not set")
        
        # Print summary
        self._print_summary()
        
        return self.valid
    
    def _check_variable(self, var_name: str, var_info: Dict[str, Any]):
        """Check a single environment variable"""
        value = os.getenv(var_name)
        is_critical = var_info.get("critical", True)
        
        if value:
            # Mask sensitive values in output
            display_value = self._mask_value(var_name, value)
            print(f"✅ {var_name}: {display_value}")
        else:
            # Check if there's a default
            default = var_info.get("default")
            if default:
                print(f"⚠️  {var_name}: Not set (using default: {default})")
                self.warnings.append(f"{var_name} not set, using default")
            else:
                if is_critical:
                    print(f"❌ {var_name}: MISSING (CRITICAL)")
                    self.errors.append(
                        f"{var_name} is missing. "
                        f"{var_info['description']}. "
                        f"Example: {var_info['example']}"
                    )
                    self.valid = False
                else:
                    print(f"⚠️  {var_name}: Not set")
                    self.warnings.append(f"{var_name} not set")
    
    def _mask_value(self, var_name: str, value: str) -> str:
        """Mask sensitive values for display"""
        sensitive_keywords = ["key", "password", "secret", "token"]
        
        if any(keyword in var_name.lower() for keyword in sensitive_keywords):
            if len(value) > 8:
                return f"{value[:4]}...{value[-4:]}"
            else:
                return "****"
        
        return value
    
    def _print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        if self.valid:
            print(f"✅ All critical variables are set!")
        else:
            print(f"❌ {len(self.errors)} critical variable(s) missing")
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warning(s)")
        
        print("="*60 + "\n")
        
        # Print errors in detail
        if self.errors:
            print("❌ ERRORS:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            print()
        
        # Print warnings
        if self.warnings:
            print("⚠️  WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            print()
        
        if not self.valid and self.strict:
            print("💡 TIP: Copy .env.example to .env and fill in your values:")
            print("   cp .env.example .env")
            print("   # Then edit .env with your actual API keys")
            print()

def validate_environment(strict: bool = True) -> bool:
    """
    Validate environment variables
    
    Args:
        strict: If True, exit on missing critical variables
    
    Returns:
        bool: True if validation passed, False otherwise
    """
    validator = EnvironmentValidator(strict=strict)
    is_valid = validator.validate()
    
    if not is_valid and strict:
        print("❌ Environment validation failed. Please fix the errors above.")
        sys.exit(1)
    
    return is_valid

if __name__ == "__main__":
    # Run validation when script is executed directly
    validate_environment(strict=True)
