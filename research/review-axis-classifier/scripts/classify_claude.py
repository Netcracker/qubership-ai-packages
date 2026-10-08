"""Classifies each PR with a Claude model through `claude -p`: no tools, no settings, the prompt in llm_prompt.py,
one call per PR. The cost is the CLI's `total_cost_usd` at list price; it includes about 3.5k tokens of CLI
overhead and the model's default thinking.

Usage: python3 classify_claude.py claude-haiku-4-5-20251001 diff24k   -> preds/claude-haiku-4-5-diff24k.jsonl
"""
import json
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from common import Preds, keys, pr_input
from llm_prompt import SYSTEM, user_prompt

DIFF = {"meta": 0, "diff24k": 24000}


def call(model, prompt):
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence", "--tools", "",
           "--setting-sources", "", "--system-prompt", SYSTEM]
    err = None
    for _ in range(3):
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=600, cwd=tempfile.gettempdir())
        try:
            d = json.loads(r.stdout)
            return d, json.loads(re.search(r"\{.*\}", d["result"], re.S).group(0))
        except (ValueError, KeyError, AttributeError) as e:
            err = f"{e}: {r.stdout[:300]} {r.stderr[:300]}"
            time.sleep(3)
    raise RuntimeError(err)


def run(model, variant):
    name = re.sub(r"-\d{8}$", "", model)          # drop the snapshot date: claude-haiku-4-5-20251001
    out = Preds(f"{name}-{variant}")

    def one(key):
        if key in out:
            return out[key]
        t = time.time()
        meta, ans = call(model, user_prompt(pr_input(key, DIFF[variant])))
        pred = {"key": key, "axes": ans["axes"], "plan": ans.get("plan"), "why": ans.get("why"),
                "cost_usd": meta["total_cost_usd"], "usage": meta["modelUsage"], "latency_s": time.time() - t}
        out.put(pred)
        return pred

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(one, keys()))
    print(model, variant, "cost $%.4f" % sum(r["cost_usd"] for r in res), file=sys.stderr)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
