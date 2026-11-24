import json
from slmbench.dataset import PROMPTS, score
from slmbench.device import detect_device
from slmbench.runtimes import DemoAdapter
from slmbench.storage import initialize, save_run, runs, models, add_model

def test_dataset_and_defined_scoring():
    assert len(PROMPTS) >= 10
    assert score("42", "42", "exact") is True
    assert score("The answer is Kyoto.", "Kyoto", "contains") is True
    assert score("A plausible summary", None, None) is None

def test_demo_explicitly_synthetic_and_deterministic():
    demo=DemoAdapter(); assert demo.mode == "synthetic"
    a=demo.generate("demo", "What is 17 + 25?")
    assert a["text"] == "42" and a["error"] is None and a["tokens"] == 1

def test_device_fields_are_explicit():
    data=detect_device()
    assert all(k in data for k in ("cpu","ram_gb","os","architecture","intel_graphics_detected","intel_graphics_user_reported","intel_acceleration","nvidia_gpu","nvidia_vram_gb","inference_target"))
    assert data["inference_target"] == "CPU (primary benchmark target)"
    assert "no acceleration claim" in data["intel_acceleration"]

def test_sqlite_round_trip(tmp_path):
    path=tmp_path/"test.db"; initialize(path)
    add_model(("Test model","family","1B","GGUF","Q4","test"),path)
    assert "Test model" in models(path).name.tolist()
    row={"created_at":"2026-01-01T00:00:00+00:00","model":"Test model","runtime":"Demo","mode":"synthetic","device_json":json.dumps({"cpu":"test"}),"config_json":json.dumps({"trials":1}),"execution_mode":"sequential","prompt_id":"p1","category":"test","prompt":"x","expected":"x","answer":"x","ttft_s":0.1,"latency_s":0.2,"generated_tokens":1,"tokens_per_second":5.0,"process_memory_mb":None,"quality_pass":1,"error":None}
    save_run(row,path); frame=runs(path)
    assert len(frame)==1 and frame.iloc[0].model=="Test model"
