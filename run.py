"""
ProduGen - Entry Point
Starts the FastAPI server.

Usage:
    python run.py
"""

import uvicorn
from backend.config import Config


def main():
    """Start the ProduGen server."""
    print("=" * 50)
    print("🚀 ProduGen - AI Product Image Generator")
    print("=" * 50)

    # Check API key status
    status = Config.validate()
    print(f"\n📋 API Key Status:")
    print(f"   Gemini API:    {'✅ Configured' if status['gemini'] else '❌ Not set'}")
    print(f"   Replicate API: {'✅ Configured' if status['replicate'] else '❌ Not set'}")

    if not status["gemini"] or not status["replicate"]:
        print(f"\n⚠️  Some API keys are missing. Edit .env file to add them.")
        print(f"   Gemini:    https://aistudio.google.com/apikey")
        print(f"   Replicate: https://replicate.com/account/api-tokens")

    print(f"\n🌐 Starting server at http://{Config.HOST}:{Config.PORT}")
    print(f"   Press Ctrl+C to stop\n")

    uvicorn.run(
        "backend.app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
    )


if __name__ == "__main__":
    main()
