"""
Interactive Sales Intelligence Agent Console.

Allows interactive natural language querying of the multi-agent platform,
testing Text-to-SQL, KPI calculations, Predictive ML tools, and RCA diagnostics
with full provenance audit trails.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure workspace root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv()

from src.agents.supervisor import SalesIntelligenceSupervisor


def print_banner():
    print("=" * 80)
    print("🤖 AI-POWERED SALES INTELLIGENCE PLATFORM — AGENTIC CONSOLE")
    print("=" * 80)
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    mode = "ONLINE (Groq)" if groq_key else ("ONLINE (OpenAI)" if openai_key else "OFFLINE (Deterministic Mock)")
    print(f"📡 Execution Mode: {mode}")
    print("\n💡 Example queries to try:")
    print("  1. [KPI]  'Show me the executive overview of revenue, order volume, and AOV'")
    print("  2. [SQL]  'What are the top 5 product categories by revenue in 2018?'")
    print("  3. [ML]   'Forecast our sales revenue for the next 30 days'")
    print("  4. [ML]   'Predict delivery delay risk for a 2kg package shipped from SP to RJ'")
    print("  5. [RCA]  'Diagnose why customer delivery delays are spiking in Southeast routes'")
    print("  6. [HYBRID] 'Why did sales drop and what is our 30-day projected forecast?'")
    print("\nCommands: 'exit' or 'quit' to close, '/offline' or '/online' to switch modes.")
    print("=" * 80 + "\n")


def main():
    print_banner()

    force_offline = False
    supervisor = SalesIntelligenceSupervisor(force_offline=force_offline)

    while True:
        try:
            user_input = input("\n💬 Enter your business question > ").strip()

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit", "q"}:
                print("\n👋 Exiting Agent Console. Goodbye!")
                break

            if user_input.lower() == "/offline":
                force_offline = True
                supervisor = SalesIntelligenceSupervisor(force_offline=True)
                print("\n⚙️ Switched to OFFLINE mode (Deterministic Mock Engine).")
                continue

            if user_input.lower() == "/online":
                force_offline = False
                supervisor = SalesIntelligenceSupervisor(force_offline=False)
                print("\n⚙️ Switched to ONLINE mode (Live LLM API).")
                continue

            print("\n⏳ Agent is analyzing and executing workflow across data marts & ML models...")
            result = supervisor.run(user_input)

            print("\n" + "-" * 80)
            print("📊 EXECUTIVE SALES INTELLIGENCE BRIEFING")
            print("-" * 80)
            print(result.get("final_response", "No response generated."))
            print("-" * 80)

        except KeyboardInterrupt:
            print("\n\n👋 Exiting Agent Console. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error processing inquiry: {e}")


if __name__ == "__main__":
    main()
