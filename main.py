import asyncio
import json
from rich import print
from rich.prompt import Prompt
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.summary_agent import SummaryAgent
from orcha_memory.memory_store import store, retrieve, list_all, compare
from dotenv import load_dotenv

load_dotenv()


async def main():
    print("[bold cyan]ORCHA — Multi-agent product feedback analysis[/bold cyan]")
    print("[dim]Commands: analyze | memory | compare | quit[/dim]\n")

    while True:
        try:
            command = Prompt.ask("[bold]ORCHA[/bold]").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n[dim]Goodbye.[/dim]")
            break

        # ── QUIT ──────────────────────────────────────────
        if command in ("quit", "exit", "q"):
            print("[dim]Goodbye.[/dim]")
            break

        # ── MEMORY ────────────────────────────────────────
        elif command == "memory":
            entries = list_all()
            if not entries:
                print("[yellow]No analyses saved yet.[/yellow]")
            else:
                print("[green]Saved analyses:[/green]")
                for entry in entries:
                    print(f"  - {entry['product']} (analyzed at {entry['analyzed_at']})")

        # ── COMPARE ───────────────────────────────────────
        elif command == "compare":
            try:
                product_a = Prompt.ask("First product").strip()
                product_b = Prompt.ask("Second product").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[dim]Cancelled.[/dim]")
                continue

            result = compare(product_a, product_b)

            if not result:
                print("[yellow]Both products must be analyzed before comparing.[/yellow]")
            else:
                print("\n[bold]Comparison:[/bold]")
                print(json.dumps(result, indent=2))

        # ── ANALYZE ───────────────────────────────────────
        elif command == "analyze" or command.startswith("analyze "):
            try:
                if command.startswith("analyze "):
                    product = command[len("analyze "):].strip()
                else:
                    product = Prompt.ask("Product name").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[dim]Cancelled.[/dim]")
                continue

            if not product:
                print("[red]Please enter a product name.[/red]")
                continue

            # check memory first
            cached = retrieve(product)
            if cached:
                print(f"[green]Found cached analysis for '{product}'[/green]")
                print(json.dumps(cached, indent=2))
                continue

            # step 1 — plan
            print(f"\n[cyan]Step 1/4 — Planning search for '{product}'...[/cyan]")
            try:
                planner = PlannerAgent()
                plan = await planner.plan(product)
                print(f"[green]Plan ready — {len(plan.get('search_queries', []))} queries[/green]")
            except Exception as e:
                print(f"[red]Planner failed: {e}[/red]")
                continue

            # step 2 — execute
            print(f"[cyan]Step 2/4 — Executing searches...[/cyan]")
            try:
                executor = ExecutorAgent()
                execution = await executor.execute(plan)
            except Exception as e:
                print(f"[red]Executor failed: {e}[/red]")
                continue

            if not execution or execution.get("total_results", 0) == 0:
                print("[yellow]No search results returned. Try a different product or check your connection.[/yellow]")
                continue

            print(f"[green]Execution done — {execution.get('total_results', 0)} results[/green]")

            # step 3 — analyze
            print(f"[cyan]Step 3/4 — Analyzing results...[/cyan]")
            try:
                analyzer = AnalyzerAgent()
                analysis = await analyzer.analyze(product, execution.get("key_findings", []))
                print(f"[green]Analysis done — sentiment: {analysis.get('sentiment', 'unknown')}[/green]")
            except Exception as e:
                print(f"[red]Analyzer failed: {e}[/red]")
                continue

            # step 4 — summarize
            print(f"[cyan]Step 4/4 — Generating summary...[/cyan]")
            try:
                summarizer = SummaryAgent()
                summary = await summarizer.summarize(analysis)
                print(f"[green]Summary ready — verdict: {summary.get('verdict', 'unknown')}[/green]")
            except Exception as e:
                print(f"[red]Summarizer failed: {e}[/red]")
                continue

            # save to memory
            store(product, summary)
            print(f"[green]Saved to memory.[/green]")

            # print final result
            print("\n[bold]Final Report:[/bold]")
            print(json.dumps(summary, indent=2))

        # ── UNKNOWN ───────────────────────────────────────
        else:
            print("[red]Unknown command. Try: analyze | memory | compare | quit[/red]")


if __name__ == "__main__":
    asyncio.run(main())