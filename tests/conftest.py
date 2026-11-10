"""pytest configuration and fixtures for all tests."""
import sys
from pathlib import Path

# Add parent directory to path so registration module can be imported
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
