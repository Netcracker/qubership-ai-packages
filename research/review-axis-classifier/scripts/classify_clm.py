"""Runs CLM-v0.1-8B locally with the questions in questions.py.

CLM's reference setup serves Qwen3-8B embeddings from vLLM on CUDA. This script computes the same last-token,
L2-normalised embeddings with transformers on Apple MPS instead, and reuses the KV cache of the shared state prefix
across questions as vLLM's --enable-prefix-caching does. The rank example of the model card (0.993) reproduces.
States are fitted into the encoder's 2048-token window by trimming the diff, then the description, then the files.

Setup (about 17 GB of downloads):
    uv venv .venv && uv pip install --python .venv/bin/python torch transformers accelerate safetensors huggingface_hub numpy requests
    git clone https://github.com/Contrastive-LM/CLM.git <clm-src>
    .venv/bin/hf download Contrastive-LM/CLM-v0.1-8B CLM_v0.1-8B.pt --local-dir <heads>
Usage:
    CLM_SRC=<clm-src> CLM_HEAD=<heads>/CLM_v0.1-8B.pt .venv/bin/python classify_clm.py profile-noul-meta [...]
    -> preds/clm-v0.1-8b-<variant>.jsonl   ("default" in the variant uses CLM's own yes/no candidates)
"""
import copy
import os
import sys
import time

import torch
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, os.path.join(os.environ["CLM_SRC"], "src"))
from clm.embedder import Embedder, l2  # noqa: E402
from clm.engine import Engine  # noqa: E402
from clm.schema import to_text  # noqa: E402

from common import Preds, keys, pr_input, profiles  # noqa: E402
from questions import noul_questions, score_questions, to_pred, variant_spec  # noqa: E402

MAX_TOKENS = 2048                 # the reference server's --max-model-len
BUDGET = MAX_TOKENS - 160         # room for the longest question appended after the state


class LocalEmbedder(Embedder):
    """Last-token pooling of Qwen3-8B's final hidden state, L2-normalised, as vLLM's pooling runner does."""

    def __init__(self):
        super().__init__(url="local", batch=64)
        self.tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
        self.tok.padding_side = "left"
        self.model = AutoModel.from_pretrained("Qwen/Qwen3-8B", dtype=torch.bfloat16).to("mps").eval()

    @torch.no_grad()
    def _fetch(self, texts):
        """States that share a long token prefix (one PR, many questions) run the prefix once."""
        ids = [self.tok(t)["input_ids"] for t in texts]
        n = 0
        while len(ids) > 1 and all(len(i) > n + 1 for i in ids) and len({i[n] for i in ids}) == 1:
            n += 1
        if n < 64 or any(len(i) > MAX_TOKENS for i in ids):
            enc = self.tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=MAX_TOKENS).to("mps")
            h = self.model(**enc).last_hidden_state[:, -1, :].float().cpu().numpy()
            return [l2(v) for v in h], int(enc["attention_mask"].sum())
        past = self.model(input_ids=torch.tensor([ids[0][:n]], device="mps"), use_cache=True).past_key_values
        out = []
        for i in ids:
            h = self.model(input_ids=torch.tensor([i[n:]], device="mps"), past_key_values=copy.deepcopy(past),
                           use_cache=True).last_hidden_state[0, -1, :]
            out.append(l2(h.float().cpu().numpy()))
        return out, sum(len(i) for i in ids)


def fit(tok, state):
    """Trims the diff, then the description, then the file list until the state fits, so that the encoder's
    truncation never cuts the title or the question."""
    pr = state["pr"]
    while len(tok(to_text(state))["input_ids"]) > BUDGET:
        if pr.get("diff"):
            pr["diff"] = pr["diff"][: int(len(pr["diff"]) * 0.8)] if len(pr["diff"]) > 200 else ""
        elif len(pr["description"]) > 300:
            pr["description"] = pr["description"][: int(len(pr["description"]) * 0.8)] + " ..."
        elif len(pr["files"]) > 10:
            pr["files"] = pr["files"][: int(len(pr["files"]) * 0.8)] + ["... more files"]
        else:
            break


if __name__ == "__main__":
    _load = torch.load
    torch.load = lambda *a, **k: _load(*a, **{**k, "weights_only": True})   # the head is a pickle: tensors only
    engine = Engine(embedder=LocalEmbedder(), checkpoint=os.environ["CLM_HEAD"], device="cpu", action_cache="0")
    for variant in sys.argv[1:]:
        with_profile, noul, diff_chars = variant_spec(variant.replace("-default", ""))
        out = Preds(f"clm-v0.1-8b-{variant}")
        for key in keys():
            if key in out:
                continue
            state = {"pr": pr_input(key, diff_chars)}
            if with_profile:
                state["project"] = profiles()[state["pr"]["repository"]]
            fit(engine.embedder.tok, state)
            qs = noul_questions() if noul else score_questions()
            if "default" in variant:          # CLM's own "Yes. This is true: ..." / "No. This is false: ..."
                qs = {k: {kk: vv for kk, vv in q.items() if kk != "criteria"} if q["type"] == "noul" else q for k, q in qs.items()}
            t = time.time()
            pred = to_pred(key, engine.answer(state, qs)["answers"], noul)
            pred.update(cost_usd=0.0, latency_s=time.time() - t)
            out.put(pred)
            print(variant, key, f"{pred['latency_s']:.1f}s", flush=True)
