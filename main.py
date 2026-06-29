#!/usr/bin/env python3
"""SENTINEL OMEGA — Entry Point"""
import os
import sys
import subprocess

from dotenv import load_dotenv
load_dotenv()


def main():
    print("=" * 60)
    print("  🛡️  SENTINEL OMEGA v3.0  🛡️")
    print("  Predictive Business Equilibrium Engine")
    print("  Multimodal Multiverse Agents on Cerebras")
    print("=" * 60)
    print()
    print("Launching War Room Dashboard...")

    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "dashboard.py")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to launch dashboard: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutdown signal received. Sentinel offline.")


if __name__ == "__main__":
    main()