"""Asks TypeSafe's Jev one request per PR with the questions in questions.py.

Usage: python3 classify_jev.py profile-noul-diff8k [score-meta ...]   -> preds/jev-<version>-<variant>.jsonl
The API key is read from TYPESAFE_API_KEY or ~/.config/typesafe/api_key. Price: $0.042 per 1M input tokens,
output free (September 2026).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from common import Preds, keys, pr_input, profiles
from questions import noul_questions, score_questions, to_pred, variant_spec

API = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
PRICE_IN = 0.042 / 1e6


def api_key():
    return os.environ.get("TYPESAFE_API_KEY") or open(os.path.expanduser("~/.config/typesafe/api_key")).read().strip()


def ask(body):
    data = json.dumps(body).encode()
    for attempt in range(6):
        req = urllib.request.Request(API, data=data, headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json",
                                                             "User-Agent": "qubership-review-axis-classifier/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if (e.code in (429, 529) or e.code >= 500) and attempt < 5:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:300]}")


def run(variant):
    with_profile, noul, diff_chars = variant_spec(variant)
    out = Preds(f"{MODEL}-{variant}")

    def one(key):
        if key in out:
            return out[key]
        state = {"pr": pr_input(key, diff_chars)}
        if with_profile:
            state["project"] = profiles()[state["pr"]["repository"]]
        t = time.time()
        resp = ask({"state": state, "model": MODEL, "questions": noul_questions() if noul else score_questions()})
        pred = to_pred(key, resp["answers"], noul)
        pred.update(usage=resp["usage"], cost_usd=resp["usage"]["input_tokens"] * PRICE_IN, latency_s=time.time() - t)
        out.put(pred)
        return pred

    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, keys()))
    print(variant, "cost $%.5f" % sum(r["cost_usd"] for r in res), file=sys.stderr)


if __name__ == "__main__":
    for v in sys.argv[1:]:
        run(v)
