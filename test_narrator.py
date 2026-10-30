"""Offline test for narrator.ask(): fake the HTTP layer, never touch the network.

Run:  .venv/bin/python test_narrator.py
"""
import json
import os
import sys

os.environ["NEBIUS_API_KEY"] = "sk-test-not-real"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import narrator  # noqa: E402

STATE = {
    "n": 2,
    "gates": [{"gate": "h", "qubits": [0]}, {"gate": "cx", "qubits": [0, 1]}],
    "probs": [0.5, 0.0, 0.0, 0.5],
    "qubits": [{"x": 0, "y": 0, "z": 0, "r": 0, "entropy": 1.0},
               {"x": 0, "y": 0, "z": 0, "r": 0, "entropy": 1.0}],
    "steps": [{"gate": "h", "qubits": [0], "probs": [0.5, 0.5, 0, 0]},
              {"gate": "cx", "qubits": [0, 1], "probs": [0.5, 0, 0, 0.5]}],
    "engine": "qiskit test",
}


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self._payload).encode()


def run(name, payload):
    narrator.urllib.request.urlopen = lambda *a, **k: FakeResp(payload)
    out = narrator.ask("why do they agree?", STATE, "en")
    print(f"[{name}] ok={out.get('ok')} reason={out.get('reason')} "
          f"text={repr(out.get('text'))[:70]} msg={repr(out.get('message'))[:110]}")
    return out


CASES = {
    "normal content": {"model": "m", "choices": [{"message": {"content": "They agree because they share one state."}}]},
    "null content + reasoning": {"model": "m", "choices": [{"message": {"content": None, "reasoning_content": "Think: the CNOT ties them."}}]},
    "empty content, length": {"model": "m", "choices": [{"message": {"content": None}, "finish_reason": "length"}]},
    "content as parts": {"model": "m", "choices": [{"message": {"content": [{"type": "text", "text": "Shared answer."}]}}]},
    "no choices": {"model": "m"},
    "choices empty": {"model": "m", "choices": []},
}

results = {name: run(name, p) for name, p in CASES.items()}

assert results["normal content"]["ok"] is True
assert results["null content + reasoning"]["ok"] is True
assert results["content as parts"]["ok"] is True
assert results["empty content, length"]["ok"] is False
assert results["no choices"]["ok"] is False
assert results["choices empty"]["ok"] is False
print("\nALL 6 CASES RETURNED WITHOUT RAISING")
