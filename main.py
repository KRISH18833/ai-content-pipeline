import argparse
from pipeline import config
from pipeline.run import run_pipeline


def main():
    p = argparse.ArgumentParser(description="AI Content Pipeline: topic -> outline -> draft -> refine")
    p.add_argument("--topic", required=True, help="Blog topic")
    p.add_argument("--tone", choices=list(config.TONES), default="casual")
    p.add_argument("--audience", default="general readers")
    p.add_argument("--length", choices=list(config.LENGTHS), default="medium")
    p.add_argument("--words", type=int, help="Custom word target (overrides --length)")
    p.add_argument("--source", help="Path to a source .txt file used for fact-checking")
    args = p.parse_args()

    r = run_pipeline(args.topic, args.tone, args.audience, args.length, args.words, args.source)

    print(f"\nSaved: {r['final_path']}")
    print(f"Words: {r['metrics_after']['words']} (target {r['outline']['total_words']})")
    print("Metrics before:", r["metrics_before"])
    print("Metrics after: ", r["metrics_after"])
    print("Report:", r["report"])


if __name__ == "__main__":
    main()
