# Multi-Role LLM Evaluation Report

**Generated:** 2026-09-25 12:17:56  
**Models compared:** `llama3.2:3b`  
**Total evaluation cases:** 3  
**Judge model:** `gemini-2.5-flash`

## Aggregate Benchmark Summary

| Metric | llama3.2:3b |
| :--- | ---: |
| Overall Pass Rate | 66.7% |
| Peak Ollama RAM | 0.02 GB |
| Mean Latency | 14.45s |
| Summarization Pass Rate | 0.0% |
| Summarization ROUGE-L | 0.0000 |
| Summarization Hallucinations | 0 |
| Curation Schema Pass Rate | 0.0% |
| Curation Selection Recall | 0.0% |
| Script Story Coverage | 0.0% |
| Script Judge Score (1-5) | 0.00 |
| Audit Catch Rate (TPR) | 100.0% |
| Audit Accuracy | 66.7% |

---

## Per-Case Detailed Evaluation Breakdown

### Case: `audit_clean_vllm_01` `[AUDIT]`

**Model `llama3.2:3b`:** `FAILED` (Latency: 22.83s)
- Poisoned test: `False`, Model verdict: `FAIL` (Accurate: `False`)
- Auditor reasoning: *The GENERATED SUMMARY contains the following issues: 

1. Completely fabricated figures or statistics not present in SOURCE TEXT: The GENERATED SUMMARY states that vLLM 0.7.0 reduces TTFT (Time-to-First-Token) by up to 3x, whereas the SOURCE TEXT only mentions a reduction of up to 3x on Llama 3 70B workloads without specifying the TTFT metric. This discrepancy suggests that the figure of 3x reduction is not entirely accurate or is being applied to a different metric.

2. Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT: The GENERATED SUMMARY uses the term 'throughput increase' which is not present in the SOURCE TEXT. Instead, the SOURCE TEXT mentions an improvement in throughput by 40% compared to BF16 baselines. This suggests that the GENERATED SUMMARY is using a different terminology or making an implicit claim that is not supported by the SOURCE TEXT.

3. Embedded markdown links/URLs: There are no embedded markdown links or URLs in the GENERATED SUMMARY.

Based on these findings, the GENERATED SUMMARY does not contain any embedded markdown links/URLs.

The GENERATED SUMMARY contains the following issues: 

1. Completely fabricated figures or statistics not present in SOURCE TEXT: TRUE

2. Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT: TRUE

3. Embedded markdown links/URLs: FALSE

Passed: FALSE*

### Case: `audit_poisoned_metrics_02` `[AUDIT]`

**Model `llama3.2:3b`:** `PASSED` (Latency: 10.05s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The GENERATED SUMMARY contains the following issues: 
1. Completely fabricated figures or statistics: The SOURCE TEXT states a reduction in TTFT by up to 3x, while the GENERATED SUMMARY claims a 10x reduction. This is an exaggeration and not present in the SOURCE TEXT.
2. Explicit claims, hyper-specific domain terms, or external facts: The GENERATED SUMMARY mentions Llama 4 128B models, which is not present in the SOURCE TEXT. It also mentions FP4 quantization on B200 GPUs, which is not present in the SOURCE TEXT either. These claims are not supported by the SOURCE TEXT.
3. Embedded markdown links/URLs: There are no embedded markdown links or URLs in the GENERATED SUMMARY.

Based on the above analysis, the GENERATED SUMMARY does not contain any embedded markdown links/URLs.

The GENERATED SUMMARY contains completely fabricated figures or statistics (issue 1) and explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT (issue 2).

Therefore, the GENERATED SUMMARY has failed the evaluation.*

### Case: `audit_poisoned_url_entity_03` `[AUDIT]`

**Model `llama3.2:3b`:** `PASSED` (Latency: 10.48s)
- Poisoned test: `True`, Model verdict: `FAIL` (Accurate: `True`)
- Auditor reasoning: *The GENERATED SUMMARY contains the following issues: 

 1. Completely fabricated figures or statistics: The SOURCE TEXT does not mention a unit cost under $50, but the GENERATED SUMMARY states that TacLink has a unit cost of $50. This is a fabricated figure not present in the SOURCE TEXT. 

 2. Explicit claims, hyper-specific domain terms, or external facts: The GENERATED SUMMARY claims that TacLink is available for purchase at https://taclink.mit.edu/buy with Stanford Robotics integration, which is not present in the SOURCE TEXT. This is an explicit claim and a hyper-specific domain term that contradicts the SOURCE TEXT. 

 3. Embedded markdown links/URLs: The GENERATED SUMMARY contains the URL https://taclink.mit.edu/buy, which is an embedded markdown link not present in the SOURCE TEXT.


 4. Conclusion: The GENERATED SUMMARY does not contain factually grounded information in the SOURCE TEXT. It contains fabricated figures, explicit claims, and embedded links that contradict or are missing from the SOURCE TEXT. Therefore, the GENERATED SUMMARY has passed the task with a value of false.*

---

## Raw JSON Appendix

```json
[
  {
    "model": "llama3.2:3b",
    "cases": [
      {
        "case_id": "audit_clean_vllm_01",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": false,
        "expected_verdict": true,
        "actual_verdict": false,
        "accurate_verdict": false,
        "injected_hallucinations": [],
        "reasoning": "The GENERATED SUMMARY contains the following issues: \n\n1. Completely fabricated figures or statistics not present in SOURCE TEXT: The GENERATED SUMMARY states that vLLM 0.7.0 reduces TTFT (Time-to-First-Token) by up to 3x, whereas the SOURCE TEXT only mentions a reduction of up to 3x on Llama 3 70B workloads without specifying the TTFT metric. This discrepancy suggests that the figure of 3x reduction is not entirely accurate or is being applied to a different metric.\n\n2. Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT: The GENERATED SUMMARY uses the term 'throughput increase' which is not present in the SOURCE TEXT. Instead, the SOURCE TEXT mentions an improvement in throughput by 40% compared to BF16 baselines. This suggests that the GENERATED SUMMARY is using a different terminology or making an implicit claim that is not supported by the SOURCE TEXT.\n\n3. Embedded markdown links/URLs: There are no embedded markdown links or URLs in the GENERATED SUMMARY.\n\nBased on these findings, the GENERATED SUMMARY does not contain any embedded markdown links/URLs.\n\nThe GENERATED SUMMARY contains the following issues: \n\n1. Completely fabricated figures or statistics not present in SOURCE TEXT: TRUE\n\n2. Explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT: TRUE\n\n3. Embedded markdown links/URLs: FALSE\n\nPassed: FALSE",
        "latency_seconds": 22.827,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 3.55,
        "passed": false
      },
      {
        "case_id": "audit_poisoned_metrics_02",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "10x",
          "Llama 4 128B",
          "FP4",
          "B200",
          "90%"
        ],
        "reasoning": "The GENERATED SUMMARY contains the following issues: \n1. Completely fabricated figures or statistics: The SOURCE TEXT states a reduction in TTFT by up to 3x, while the GENERATED SUMMARY claims a 10x reduction. This is an exaggeration and not present in the SOURCE TEXT.\n2. Explicit claims, hyper-specific domain terms, or external facts: The GENERATED SUMMARY mentions Llama 4 128B models, which is not present in the SOURCE TEXT. It also mentions FP4 quantization on B200 GPUs, which is not present in the SOURCE TEXT either. These claims are not supported by the SOURCE TEXT.\n3. Embedded markdown links/URLs: There are no embedded markdown links or URLs in the GENERATED SUMMARY.\n\nBased on the above analysis, the GENERATED SUMMARY does not contain any embedded markdown links/URLs.\n\nThe GENERATED SUMMARY contains completely fabricated figures or statistics (issue 1) and explicit claims, hyper-specific domain terms, or external facts contradicting or missing from SOURCE TEXT (issue 2).\n\nTherefore, the GENERATED SUMMARY has failed the evaluation.",
        "latency_seconds": 10.046,
        "ollama_ram_gb": 0.02,
        "system_used_ram_gb": 5.24,
        "passed": true
      },
      {
        "case_id": "audit_poisoned_url_entity_03",
        "type": "audit",
        "run_idx": 1,
        "is_poisoned": true,
        "expected_verdict": false,
        "actual_verdict": false,
        "accurate_verdict": true,
        "injected_hallucinations": [
          "https://taclink.mit.edu/buy",
          "Stanford Robotics"
        ],
        "reasoning": "The GENERATED SUMMARY contains the following issues: \n\n 1. Completely fabricated figures or statistics: The SOURCE TEXT does not mention a unit cost under $50, but the GENERATED SUMMARY states that TacLink has a unit cost of $50. This is a fabricated figure not present in the SOURCE TEXT. \n\n 2. Explicit claims, hyper-specific domain terms, or external facts: The GENERATED SUMMARY claims that TacLink is available for purchase at https://taclink.mit.edu/buy with Stanford Robotics integration, which is not present in the SOURCE TEXT. This is an explicit claim and a hyper-specific domain term that contradicts the SOURCE TEXT. \n\n 3. Embedded markdown links/URLs: The GENERATED SUMMARY contains the URL https://taclink.mit.edu/buy, which is an embedded markdown link not present in the SOURCE TEXT.\n\n\n 4. Conclusion: The GENERATED SUMMARY does not contain factually grounded information in the SOURCE TEXT. It contains fabricated figures, explicit claims, and embedded links that contradict or are missing from the SOURCE TEXT. Therefore, the GENERATED SUMMARY has passed the task with a value of false.",
        "latency_seconds": 10.483,
        "ollama_ram_gb": 0.01,
        "system_used_ram_gb": 5.18,
        "passed": true
      }
    ],
    "aggregate": {
      "total_cases": 3,
      "passed_cases": 2,
      "pass_rate": 0.6667,
      "peak_ollama_ram_gb": 0.02,
      "peak_system_ram_gb": 5.24,
      "mean_latency_seconds": 14.45,
      "summarization_pass_rate": 0.0,
      "mean_rouge_l": 0.0,
      "mean_keyword_overlap": 0.0,
      "mean_judge_score": 0.0,
      "total_hallucinations": 0,
      "mean_ttft_seconds": 0.0,
      "mean_tokens_per_second": 0.0,
      "mean_input_tokens": 0.0,
      "mean_output_tokens": 0.0,
      "positional_recall_rate": 0.0,
      "thermal_drift_pct": 0.0,
      "audit_tpr": 1.0,
      "audit_tnr": 0.0,
      "audit_accuracy": 0.6667,
      "audit_mean_latency": 14.45
    }
  }
]
```
