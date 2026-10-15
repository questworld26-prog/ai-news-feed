"""
Pipeline Telemetry & Performance Monitoring.
Tracks execution duration, process RSS memory, memory deltas,
system RAM consumption, and stage-specific throughput metrics.
"""

from __future__ import annotations

import os
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

try:
    import psutil
except ImportError:
    psutil = None

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


@dataclass
class StageRecord:
    name: str
    duration_s: float
    mem_start_mb: float
    mem_end_mb: float
    mem_delta_mb: float
    system_ram_pct: float
    metrics: dict[str, Any] = field(default_factory=dict)


class StageContext:
    def __init__(self, name: str, tracker: PipelineTracker):
        self.name = name
        self.tracker = tracker
        self.metrics: dict[str, Any] = {}

    def set_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value

    def update_metrics(self, data: dict[str, Any]) -> None:
        self.metrics.update(data)


class PipelineTracker:
    """Tracks and reports performance, memory, and throughput metrics across pipeline stages."""

    def __init__(self):
        self.process = psutil.Process(os.getpid()) if psutil else None
        self.records: list[StageRecord] = []
        self.pipeline_start_t = time.perf_counter()
        self.console = Console() if _HAS_RICH else None

    def get_current_rss_mb(self) -> float:
        if self.process:
            try:
                return round(self.process.memory_info().rss / (1024 * 1024), 2)
            except Exception:
                return 0.0
        return 0.0

    def get_system_ram_pct(self) -> float:
        if psutil:
            try:
                return psutil.virtual_memory().percent
            except Exception:
                return 0.0
        return 0.0

    @contextmanager
    def track_stage(
        self, name: str, initial_metrics: dict[str, Any] | None = None
    ) -> Generator[StageContext, None, None]:
        """Context manager to measure time and memory usage for a pipeline stage."""
        ctx = StageContext(name, self)
        if initial_metrics:
            ctx.update_metrics(initial_metrics)

        mem_start = self.get_current_rss_mb()
        t_start = time.perf_counter()

        try:
            yield ctx
        finally:
            duration = time.perf_counter() - t_start
            mem_end = self.get_current_rss_mb()
            mem_delta = round(mem_end - mem_start, 2)
            ram_pct = self.get_system_ram_pct()

            record = StageRecord(
                name=name,
                duration_s=duration,
                mem_start_mb=mem_start,
                mem_end_mb=mem_end,
                mem_delta_mb=mem_delta,
                system_ram_pct=ram_pct,
                metrics=dict(ctx.metrics),
            )
            self.records.append(record)
            self.print_stage_card(record)

    def print_stage_card(self, record: StageRecord) -> None:
        """Prints a styled telemetry card after a stage finishes."""
        delta_str = f"+{record.mem_delta_mb:.2f} MB" if record.mem_delta_mb >= 0 else f"{record.mem_delta_mb:.2f} MB"
        time_str = f"{record.duration_s:.2f}s" if record.duration_s >= 1.0 else f"{record.duration_s * 1000:.0f}ms"

        custom_stats = []
        for k, v in record.metrics.items():
            k_clean = k.replace("_", " ").title()
            custom_stats.append(f"{k_clean}: [bold cyan]{v}[/bold cyan]")
        custom_str = " | ".join(custom_stats) if custom_stats else "Done"

        if self.console and _HAS_RICH:
            card_content = (
                f"[bold white]⏱️  Duration:[/bold white] [bold green]{time_str}[/bold green]   "
                f"[bold white]💾 Memory RSS:[/bold white] [bold yellow]{record.mem_end_mb:.1f} MB[/bold yellow] ([italic]{delta_str}[/italic])   "
                f"[bold white]🖥️  System RAM:[/bold white] [dim]{record.system_ram_pct}%[/dim]\n"
                f"[bold white]📊 Metrics:[/bold white] {custom_str}"
            )
            self.console.print(
                Panel(
                    card_content,
                    title=f"[bold cyan]STAGE METRICS: {record.name}[/bold cyan]",
                    border_style="blue",
                    padding=(0, 2),
                )
            )
        else:
            print(f"\n--- STAGE STATS: {record.name} ---")
            print(
                f"Time Taken: {time_str} | Memory: {record.mem_end_mb:.1f} MB ({delta_str}) | System RAM: {record.system_ram_pct}%"
            )
            if record.metrics:
                print(f"Metrics: {record.metrics}")
            print("---------------------------------\n")

    def print_summary_dashboard(self) -> None:
        """Prints a final pipeline performance and memory breakdown dashboard."""
        total_time = time.perf_counter() - self.pipeline_start_t
        current_mem = self.get_current_rss_mb()
        peak_mem = max([r.mem_end_mb for r in self.records] + [current_mem])

        if self.console and _HAS_RICH:
            table = Table(
                title=f"🚀 AI BRIEFING PIPELINE TELEMETRY DASHBOARD (Total Time: {total_time:.2f}s | Peak RSS: {peak_mem:.1f} MB)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Stage / Phase", style="cyan", no_wrap=True)
            table.add_column("Time Taken", justify="right", style="green")
            table.add_column("% Total", justify="right", style="dim")
            table.add_column("Process RSS", justify="right", style="yellow")
            table.add_column("Mem Δ", justify="right", style="magenta")
            table.add_column("Key Stage Highlights", style="white")

            for r in self.records:
                pct = (r.duration_s / total_time * 100) if total_time > 0 else 0
                time_str = f"{r.duration_s:.2f}s" if r.duration_s >= 1.0 else f"{r.duration_s * 1000:.0f}ms"
                delta_str = f"+{r.mem_delta_mb:.1f} MB" if r.mem_delta_mb >= 0 else f"{r.mem_delta_mb:.1f} MB"

                metrics_summary = ", ".join(f"{k}: {v}" for k, v in list(r.metrics.items())[:3])
                table.add_row(
                    r.name,
                    time_str,
                    f"{pct:.1f}%",
                    f"{r.mem_end_mb:.1f} MB",
                    delta_str,
                    metrics_summary or "Completed",
                )

            self.console.print("\n")
            self.console.print(table)
            self.console.print("\n")
        else:
            print("\n================ PIPELINE PERFORMANCE DASHBOARD ================")
            print(f"Total Time: {total_time:.2f}s | Peak RSS Memory: {peak_mem:.1f} MB")
            for r in self.records:
                time_str = f"{r.duration_s:.2f}s" if r.duration_s >= 1.0 else f"{r.duration_s * 1000:.0f}ms"
                delta_str = f"+{r.mem_delta_mb:.1f} MB" if r.mem_delta_mb >= 0 else f"{r.mem_delta_mb:.1f} MB"
                print(f"  • {r.name:<35} | {time_str:<8} | Mem: {r.mem_end_mb:.1f} MB ({delta_str:<9}) | {r.metrics}")
            print("=================================================================\n")
