

import json
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

BENCHMARK_DIR=Path(__file__).parent
DATASET_DIR=BENCHMARK_DIR/"dataset"
LABELS_FILE=DATASET_DIR/"labels.json"
RESULTS_DIR=BENCHMARK_DIR/"results"
RESULTS_DIR.mkdir(exist_ok=True)

def load_labels()->dict:
    """Load the ground truth answer key from labels.json."""
    with open(LABELS_FILE)as f:
        return json.load(f)

def run_semgrep(file_path:Path)->list[dict]:
    """Run Semgrep on a single file, return list of findings."""
    result=subprocess.run(
        ["uv","run","semgrep","--config","p/python","--json",str(file_path)],
        capture_output=True,text=True,timeout=60,
    )

    if result.returncode not in (0,1):
        print(f"  ⚠️  Semgrep error: {result.stderr[:200]}")
        return []
    try:
        data=json.loads(result.stdout)
        return [
            {
                "scanner":"semgrep",
                "rule_id":r.get("check_id","unknown"),
                "line":r.get("start",{}).get("line",0),
                "severity":r.get("extra",{}).get("severity","unknown"),
                "message":r.get("extra",{}).get("message",""),
            }
            for r in data.get("results",[])
        ]
    except json.JSONDecodeError:
        return []

def run_bandit(file_path:Path)->list[dict]:
    """Run Bandit on a single file, return list of findings."""
    result=subprocess.run(
        ["uv","run","bandit",'-f',"json",str(file_path)],
        capture_output=True,text=True,timeout=60,
    )
    try:
        data=json.loads(result.stdout)
        return [
            {
                "scanner":"bandit",
                "rule_id":r.get("test_id","unknown"),
                "line":r.get("line_number",0),
                "severity":r.get("issue_severity","unknown").lower(),
                "message":r.get("issue_text",""),
            }
            for r in data.get("results",[])
        ]
    except json.JSONDecodeError:
        return []

def run_benchmark()->dict:
    """Run all scanners on all labeled samples, return structured results."""
    print("🔍 Loading benchmark dataset...")
    labels_data=load_labels()
    samples=labels_data["samples"]
    run_id=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    results={
        "run_id":run_id,
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "dataset_version":labels_data["version"],
        "sample_results":[],
    }

    print(f"📂 Scanning {len(samples)} samples...\n")


    for sample in samples:
        sample_file=DATASET_DIR/ sample["file"]
        if not sample_file.exists():
            print(f"  ❌ File not found: {sample_file}")
            continue

        print(f"  📄 [{sample['id']}] Scanning {sample_file.name}...")
        all_findings=run_semgrep(sample_file) + run_bandit(sample_file)
        detected=len(all_findings)>0

        results["sample_results"].append({
            "sample_id": sample["id"],
            "file": sample["file"],
            "is_false_positive_sample": sample["is_false_positive"],
            "expected_vulnerability": sample["vulnerability_type"],
            "expected_cwe": sample["cwe"],
            "vulnerable_lines": sample.get("vulnerable_lines", sample.get("vulnerability_lines", [])),
            "detected": detected,
            "finding_count": len(all_findings),
            "findings": all_findings,
        })

        if sample["is_false_positive"]:
            status = "⚠️  FALSE POSITIVE (safe code flagged!)" if detected else "✅ TRUE NEGATIVE (safe code correctly ignored)"
        else:
            status="✅ DETECTED" if detected else "❌ MISSED"
        
        print(f"     → {status} | {len(all_findings)} finding(s)")
    return results

def calculate_metrics(results:dict)->dict:
    """Calculate recall, FP rate from benchmark results."""
    sample_results=results["sample_results"]
    real_vuln=[s for s in sample_results if not s["is_false_positive_sample"]]
    fp_tests=[s for s in sample_results if s["is_false_positive_sample"]]

    tp=sum(1 for s in real_vuln if s["detected"])
    fn=sum(1 for s in real_vuln if not s["detected"])
    fp=sum(1 for s in fp_tests if s["detected"])
    tn=sum(1 for s in fp_tests if not s["detected"])

    recall=tp/max(tp+fn,1)
    fp_rate=fp/max(fp+tn,1)

    return{
        "total_samples": len(sample_results),
        "true_positives": tp, "false_negatives": fn,
        "false_positives": fp, "true_negatives": tn,
        "recall_pct": round(recall * 100, 1),
        "fp_rate_pct": round(fp_rate * 100, 1),
        "target_recall_pct": 80.0,
        "target_fp_rate_pct": 15.0,
        "recall_passed": recall >= 0.80,
        "fp_rate_passed": fp_rate <= 0.15,
    }

def print_report(results:dict,metrics:dict)->None:
    """Print a human-readable benchmark report."""
    print("\n" + "=" * 60)
    print("📊 BENCHMARK RESULTS REPORT")
    print("=" * 60)
    print(f"Run ID:    {results['run_id']}")
    print(f"Samples:   {metrics['total_samples']} total")
    print()
    print("ACCURACY METRICS:")
    print(f"  Recall:     {metrics['recall_pct']}%  [target: >{metrics['target_recall_pct']}%]  {'✅' if metrics['recall_passed'] else '❌'}")
    print(f"  FP Rate:    {metrics['fp_rate_pct']}%  [target: <{metrics['target_fp_rate_pct']}%]  {'✅' if metrics['fp_rate_passed'] else '❌'}")
    print()
    print("CONFUSION MATRIX:")
    print(f"  True Positives:  {metrics['true_positives']}  (real bugs found)")
    print(f"  False Negatives: {metrics['false_negatives']}  (real bugs missed)")
    print(f"  False Positives: {metrics['false_positives']}  (safe code flagged)")
    print(f"  True Negatives:  {metrics['true_negatives']}  (safe code correctly ignored)")
    print()
    overall = metrics["recall_passed"] and metrics["fp_rate_passed"]
    print("🏆 OVERALL: PASSED!" if overall else "⚠️  OVERALL: Needs improvement — check missed cases above.")
    print("=" * 60)

def main():
    print("🚀 AI Security Analyst Platform — Benchmark Runner")
    print("=" * 60)
    results=run_benchmark()
    metrics=calculate_metrics(results)
    results["metrics"]=metrics

    output_path=RESULTS_DIR / f"run_{results['run_id']}.json"
    with open(output_path,"w") as f:
        json.dump(results,f, indent=2)
    
    print_report(results,metrics)
    print(f"\n💾 Full results saved to: {output_path}")

    if not (metrics["recall_passed"] and metrics["fp_rate_passed"]):
        sys.exit(1)


if __name__=="__main__":
    main()