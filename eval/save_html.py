"""
HTML Dashboard Generator Module for Model Comparison.
Renders an interactive, visually rich HTML report with Chart.js charts.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def save_html_dashboard(
    all_results: list[dict[str, Any]],
    config: dict[str, Any],
    project_root: Path | None = None,
) -> Path:
    """Generate a rich, interactive HTML dashboard with Chart.js visualization for model comparison."""
    if project_root is None:
        project_root = Path(__file__).parent.parent
    report_dir = project_root / config["output"]["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = report_dir / f"model_comparison_{timestamp}.html"

    models = [r["model"] for r in all_results]
    n_cases = all_results[0]["aggregate"]["total_cases"] if all_results else 0
    raw_json_str = json.dumps(all_results, indent=2, default=str)
    eval_runs = config["evaluation"].get("eval_runs", 1)
    judge_model = config["judge"]["model"]

    # Build model table header columns
    model_th_elements = "".join(
        [f'<th class="px-6 py-4 font-semibold text-center text-cyan-400">{m}</th>' for m in models]
    )

    html_template = (
        """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Summarization Benchmark Dashboard</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#f0f9ff',
                            500: '#06b6d4',
                            600: '#0891b2',
                            900: '#164e63',
                        },
                        darkcard: '#1e293b',
                        darkbg: '#0f172a',
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body class="min-h-screen pb-12">
    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex flex-wrap justify-between items-center gap-4">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                </div>
                <div>
                    <h1 class="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">LLM Summarization Model Comparison</h1>
                    <p class="text-xs text-slate-400">Benchmark Dashboard • """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """</p>
                </div>
            </div>
            <div class="flex items-center gap-3 text-xs text-slate-400 bg-slate-800/60 px-4 py-2 rounded-xl border border-slate-700/50">
                <span>Judge: <strong class="text-slate-200">"""
        + str(judge_model)
        + """</strong></span>
                <span class="text-slate-600">•</span>
                <span>Cases: <strong class="text-slate-200">"""
        + str(n_cases)
        + """</strong></span>
                <span class="text-slate-600">•</span>
                <span>Runs/case: <strong class="text-slate-200">"""
        + str(eval_runs)
        + """</strong></span>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 mt-8 space-y-8">
        <!-- Top Executive KPI Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="glass-card p-5 rounded-2xl">
                <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Models Evaluated</div>
                <div class="text-3xl font-extrabold text-white mt-1">"""
        + str(len(models))
        + """</div>
                <div class="text-xs text-cyan-400 mt-2 truncate">"""
        + ", ".join(models)
        + """</div>
            </div>
            <div class="glass-card p-5 rounded-2xl">
                <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Top Pass Rate Model</div>
                <div id="top-pass-model" class="text-2xl font-extrabold text-emerald-400 mt-1">-</div>
                <div id="top-pass-score" class="text-xs text-slate-400 mt-2">-</div>
            </div>
            <div class="glass-card p-5 rounded-2xl">
                <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Fastest TTFT Model</div>
                <div id="fastest-ttft-model" class="text-2xl font-extrabold text-amber-400 mt-1">-</div>
                <div id="fastest-ttft-score" class="text-xs text-slate-400 mt-2">-</div>
            </div>
            <div class="glass-card p-5 rounded-2xl">
                <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Lowest Ollama RAM</div>
                <div id="lowest-ram-model" class="text-2xl font-extrabold text-purple-400 mt-1">-</div>
                <div id="lowest-ram-score" class="text-xs text-slate-400 mt-2">-</div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Radar Chart: Multi-axis Quality Comparison -->
            <div class="glass-card p-6 rounded-2xl flex flex-col">
                <h2 class="text-base font-bold text-slate-200 mb-1">Quality & Accuracy Profile (Radar)</h2>
                <p class="text-xs text-slate-400 mb-4">Normalized score comparison across Pass Rate, ROUGE-L, Overlap, Judge, and Positional Recall.</p>
                <div class="relative flex-1 min-h-[300px]">
                    <canvas id="qualityRadarChart"></canvas>
                </div>
            </div>

            <!-- Bar Chart: Latency & Speed -->
            <div class="glass-card p-6 rounded-2xl flex flex-col">
                <h2 class="text-base font-bold text-slate-200 mb-1">Latency (TTFT vs Total) & Speed</h2>
                <p class="text-xs text-slate-400 mb-4">Time-to-First-Token (s), Total Latency (s), and Generation Speed (tok/s).</p>
                <div class="relative flex-1 min-h-[300px]">
                    <canvas id="latencyBarChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Comprehensive Aggregate Metrics Table -->
        <div class="glass-card rounded-2xl overflow-hidden">
            <div class="p-6 border-b border-slate-800">
                <h2 class="text-lg font-bold text-white">Full Production Checklist Metric Comparison</h2>
                <p class="text-xs text-slate-400 mt-1">Side-by-side performance evaluation against target thresholds.</p>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-300">
                    <thead class="bg-slate-900/80 text-xs uppercase text-slate-400 border-b border-slate-800">
                        <tr>
                            <th class="px-6 py-4 font-semibold">Metric / Category</th>
                            <th class="px-6 py-4 font-semibold text-center">Target Threshold</th>
                            """
        + model_th_elements
        + """
                        </tr>
                    </thead>
                    <tbody id="metrics-table-body" class="divide-y divide-slate-800/60 font-mono text-xs">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Case-by-Case Deep Dive Breakdown -->
        <div class="glass-card p-6 rounded-2xl space-y-4">
            <h2 class="text-lg font-bold text-white">Per-Case Generation & Judge Breakdown</h2>
            <p class="text-xs text-slate-400">Inspect candidate summaries, detected hallucinations, and Gemini judge reasoning per test article.</p>
            <div id="cases-container" class="space-y-4 mt-4"></div>
        </div>
    </main>

    <script>
        const evalData = """
        + raw_json_str
        + """;

        function initKPIs() {
            if (!evalData.length) return;

            const bestPass = [...evalData].sort((a, b) => b.aggregate.pass_rate - a.aggregate.pass_rate)[0];
            document.getElementById('top-pass-model').innerText = bestPass.model;
            document.getElementById('top-pass-score').innerText = `${(bestPass.aggregate.pass_rate * 100).toFixed(1)}% pass rate`;

            const fastestTTFT = [...evalData].sort((a, b) => a.aggregate.mean_ttft_seconds - b.aggregate.mean_ttft_seconds)[0];
            document.getElementById('fastest-ttft-model').innerText = fastestTTFT.model;
            document.getElementById('fastest-ttft-score').innerText = `${fastestTTFT.aggregate.mean_ttft_seconds.toFixed(2)}s avg TTFT`;

            const lowestRAM = [...evalData].sort((a, b) => (a.aggregate.peak_ollama_ram_gb || 0) - (b.aggregate.peak_ollama_ram_gb || 0))[0];
            document.getElementById('lowest-ram-model').innerText = lowestRAM.model;
            document.getElementById('lowest-ram-score').innerText = `${(lowestRAM.aggregate.peak_ollama_ram_gb || 0).toFixed(2)} GB Ollama RAM`;
        }

        function initRadarChart() {
            const ctx = document.getElementById('qualityRadarChart').getContext('2d');
            const colors = [
                { border: '#06b6d4', bg: 'rgba(6, 182, 212, 0.2)' },
                { border: '#10b981', bg: 'rgba(16, 185, 129, 0.2)' },
                { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.2)' },
                { border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.2)' },
            ];

            const datasets = evalData.map((d, i) => ({
                label: d.model,
                data: [
                    d.aggregate.pass_rate * 100,
                    (d.aggregate.mean_rouge_l || 0) * 100,
                    (d.aggregate.mean_keyword_overlap || 0) * 100,
                    ((d.aggregate.mean_judge_score || 0) / 5) * 100,
                    (d.aggregate.positional_recall_rate || 0) * 100
                ],
                borderColor: colors[i % colors.length].border,
                backgroundColor: colors[i % colors.length].bg,
                borderWidth: 2,
                pointBackgroundColor: colors[i % colors.length].border,
            }));

            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Pass Rate (%)', 'ROUGE-L (x100)', 'Keyword Overlap (%)', 'Judge Score (%)', 'Positional Recall (%)'],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            pointLabels: { color: '#94a3b8', font: { size: 11 } },
                            ticks: { color: '#64748b', backdropColor: 'transparent', min: 0, max: 100 }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#f8fafc' } }
                    }
                }
            });
        }

        function initBarChart() {
            const ctx = document.getElementById('latencyBarChart').getContext('2d');
            const labels = evalData.map(d => d.model);

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Mean TTFT (s)',
                            data: evalData.map(d => d.aggregate.mean_ttft_seconds),
                            backgroundColor: '#f59e0b',
                            borderRadius: 6
                        },
                        {
                            label: 'Total Latency (s)',
                            data: evalData.map(d => d.aggregate.mean_latency_seconds),
                            backgroundColor: '#06b6d4',
                            borderRadius: 6
                        },
                        {
                            label: 'Speed (tok/s)',
                            data: evalData.map(d => d.aggregate.mean_tokens_per_second),
                            backgroundColor: '#10b981',
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: {
                        legend: { labels: { color: '#f8fafc' } }
                    }
                }
            });
        }

        function initTable() {
            const tbody = document.getElementById('metrics-table-body');
            const rows = [
                { key: 'pass_rate', name: 'Pass Rate', target: '>= 80%', fmt: v => `${(v * 100).toFixed(1)}%` },
                { key: 'peak_ollama_ram_gb', name: 'Memory Footprint (Ollama RAM)', target: '< 5.0 GB', fmt: v => `${v.toFixed(2)} GB` },
                { key: 'peak_system_ram_gb', name: 'Memory Footprint (Total System RAM)', target: 'Informational', fmt: v => `${v.toFixed(2)} GB` },
                { key: 'mean_ttft_seconds', name: 'Latency TTFT', target: '< 0.60 s', fmt: v => `${v.toFixed(2)} s` },
                { key: 'mean_latency_seconds', name: 'Total Latency', target: '< 3.0 s', fmt: v => `${v.toFixed(2)} s` },
                { key: 'mean_rouge_l', name: 'Lexical Overlap (ROUGE-L)', target: '>= 0.45', fmt: v => v.toFixed(4) },
                { key: 'mean_keyword_overlap', name: 'Keyword Overlap Score', target: '>= 0.35', fmt: v => v.toFixed(2) },
                { key: 'mean_judge_score', name: 'Semantic Judge Score', target: '>= 4.0 / 5', fmt: v => `${v.toFixed(2)} / 5` },
                { key: 'total_hallucinations', name: 'Total Hallucinations', target: '0', fmt: v => v },
                { key: 'positional_recall_rate', name: 'Positional Recall Rate', target: '100%', fmt: v => `${(v * 100).toFixed(0)}%` },
                { key: 'thermal_drift_pct', name: 'Thermal Stability Drift', target: '< 15%', fmt: v => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` },
                { key: 'mean_tokens_per_second', name: 'Generation Speed', target: 'Maximized', fmt: v => `${v.toFixed(1)} tok/s` },
                { key: 'tokens_in_out', name: 'Tokens (Prompt / Summary)', target: 'Informational', fmt: (v, d) => `${Math.round(d.aggregate.mean_input_tokens)} / ${Math.round(d.aggregate.mean_output_tokens)}` }
            ];

            let html = '';
            rows.forEach(r => {
                html += `<tr class="hover:bg-slate-800/40 transition">
                    <td class="px-6 py-3 font-medium text-slate-200">${r.name}</td>
                    <td class="px-6 py-3 text-center text-slate-400">${r.target}</td>`;
                evalData.forEach(d => {
                    const val = r.key === 'tokens_in_out' ? '' : d.aggregate[r.key];
                    const formatted = r.fmt(val, d);
                    html += `<td class="px-6 py-3 text-center font-bold text-cyan-300">${formatted}</td>`;
                });
                html += `</tr>`;
            });
            tbody.innerHTML = html;
        }

        function initCases() {
            const container = document.getElementById('cases-container');
            if (!evalData.length || !evalData[0].cases.length) return;

            const casesMap = {};
            evalData.forEach(d => {
                d.cases.forEach(c => {
                    if (!casesMap[c.case_id]) casesMap[c.case_id] = [];
                    casesMap[c.case_id].push({ model: d.model, case: c });
                });
            });

            let html = '';
            Object.keys(casesMap).forEach(caseId => {
                const items = casesMap[caseId];
                html += `
                <div class="border border-slate-800 bg-slate-900/40 rounded-xl p-5 space-y-4">
                    <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                        <h3 class="text-sm font-bold text-cyan-400">Case ID: ` + caseId + `</h3>
                        <span class="text-xs text-slate-500">${items.length} Model Summaries</span>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">`;

                items.forEach(item => {
                    const c = item.case;
                    const passBadge = c.passed
                        ? `<span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-bold">PASS</span>`
                        : `<span class="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded text-[10px] font-bold">FAIL</span>`;

                    html += `
                    <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 flex flex-col justify-between space-y-3">
                        <div>
                            <div class="flex justify-between items-center mb-2">
                                <span class="font-bold text-slate-200 text-xs">${item.model}</span>
                                ${passBadge}
                            </div>
                            <p class="text-xs text-slate-300 italic border-l-2 border-cyan-500/50 pl-2 py-1 mb-2 bg-slate-900/40 rounded-r">
                                "${c.summary}"
                            </p>
                            <p class="text-[11px] text-slate-400">
                                <strong>Judge:</strong> ${c.judge_reasoning}
                            </p>
                        </div>
                        <div class="pt-2 border-t border-slate-700/50 flex flex-wrap gap-2 text-[10px] text-slate-400 font-mono">
                            <span>ROUGE: <strong class="text-slate-200">${c.rouge_l.toFixed(3)}</strong></span>
                            <span>Overlap: <strong class="text-slate-200">${c.keyword_overlap.toFixed(2)}</strong></span>
                            <span>TTFT: <strong class="text-slate-200">${c.ttft_seconds.toFixed(2)}s</strong></span>
                        </div>
                    </div>`;
                });

                html += `</div></div>`;
            });
            container.innerHTML = html;
        }

        window.addEventListener('DOMContentLoaded', () => {
            initKPIs();
            initRadarChart();
            initBarChart();
            initTable();
            initCases();
        });
    </script>
</body>
</html>"""
    )

    html_path.write_text(html_template, encoding="utf-8")
    return html_path
