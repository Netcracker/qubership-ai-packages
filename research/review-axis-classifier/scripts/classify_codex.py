"""Classifies each PR with an OpenAI model through `codex exec`, with the prompt in llm_prompt.py as the model
instructions, MCP servers and web search off, a read-only sandbox, one call per PR. Codex adds about 18k input
tokens of its own per call; most are cached.

Usage: python3 classify_codex.py gpt-6-luna high diff24k   -> preds/gpt-6-luna-high-diff24k.jsonl
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from common import CACHE, Preds, keys, pr_input
from llm_prompt import SYSTEM, user_prompt

# USD per token, list prices (September 2026); reasoning tokens bill as output.
PRICE = {"gpt-6-luna": {"in": 0.10e-6, "cached": 0.01e-6, "out": 0.50e-6}}
DIFF = {"meta": 0, "diff24k": 24000}


def call(model, effort, prompt, sys_file):
    cmd = ["codex", "exec", "-m", model, "-c", f"model_reasoning_effort={effort}", "-c", "mcp_servers={}",
           "-c", f"model_instructions_file={sys_file}", "-c", "tools.web_search=false", "--json",
           "--skip-git-repo-check", "--sandbox", "read-only", "--ephemeral", "-"]
    err = None
    for _ in range(3):
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=900, cwd=tempfile.gettempdir())
        events = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
        msgs = [e["item"]["text"] for e in events if e.get("type") == "item.completed" and e["item"].get("type") == "agent_message"]
        usage = [e["usage"] for e in events if e.get("type") == "turn.completed"]
        kinds = {}
        for e in events:
            if e.get("type") == "item.completed":
                kinds[e["item"].get("type")] = kinds.get(e["item"].get("type"), 0) + 1
        try:
            u = dict(usage[-1], items=kinds)
            return u, json.loads(re.search(r"\{.*\}", msgs[-1], re.S).group(0))
        except (IndexError, ValueError, AttributeError) as e:
            err = f"{e}: {r.stdout[-300:]} {r.stderr[-300:]}"
            time.sleep(5)
    raise RuntimeError(err)


def cost(model, u):
    p = PRICE[model]
    cached = u["cached_input_tokens"]
    return (u["input_tokens"] - cached) * p["in"] + cached * p["cached"] + (u["output_tokens"] + u.get("reasoning_output_tokens", 0)) * p["out"]


def run(model, effort, variant):
    out = Preds(f"{model}-{effort}-{variant}")
    os.makedirs(CACHE, exist_ok=True)
    sys_file = os.path.join(CACHE, "codex_system.txt")
    open(sys_file, "w").write(SYSTEM)

    def one(key):
        if key in out:
            return out[key]
        t = time.time()
        u, ans = call(model, effort, user_prompt(pr_input(key, DIFF[variant])), sys_file)
        pred = {"key": key, "axes": ans["axes"], "plan": ans.get("plan"), "why": ans.get("why"), "usage": u,
                "cost_usd": cost(model, u), "latency_s": time.time() - t}
        out.put(pred)
        return pred

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(one, keys()))
    print(model, effort, variant, "cost $%.4f" % sum(r["cost_usd"] for r in res), file=sys.stderr)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
