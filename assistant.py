#!/usr/bin/env python3
import sys
from frankenstein_ai.router import route_and_run
from frankenstein_ai.utils.merge import merge_outputs
from frankenstein_ai.memory.memory import Memory
from frankenstein_ai.corrector.corrector import simple_correct

def main():
    if len(sys.argv) < 2:
        print("Usage: python assistant.py \"your prompt here\"")
        sys.exit(1)
    prompt = sys.argv[1]

    # Correct the prompt
    corrected_prompt = simple_correct(prompt)

    # Memory recall
    mem = Memory()
    recalls = mem.search(corrected_prompt, limit=3)

    # Route and run boosters in parallel
    results = route_and_run(corrected_prompt)

    # Merge results
    merged = merge_outputs(corrected_prompt, recalls, results)

    # Store interaction in memory
    mem.save_interaction(corrected_prompt, merged.get("text",""))

    print("\n=== Frankenstein AI v0.1 ===")
    print(f"Prompt: {prompt}")
    if corrected_prompt != prompt:
        print(f"Corrected: {corrected_prompt}")
    print("\n--- Output ---")
    print(merged.get("text","(no text)"))
    if merged.get("artifacts"):
        print("\nArtifacts:")
        for k,v in merged["artifacts"].items():
            print(f" - {k}: {v}")
    if merged.get("sources"):
        print("\nSources:")
        for s in merged["sources"]:
            print(f" - {s}")

if __name__ == "__main__":
    main()
