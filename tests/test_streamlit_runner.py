from pathlib import Path
from streamlit.testing.v1 import AppTest
from slmbench.runtimes import OllamaAdapter


def test_benchmark_runner_preserves_settings_and_renders_without_deltagenerator(monkeypatch):
    monkeypatch.setattr(OllamaAdapter, "available", lambda self: (True, "Ollama API reachable"))
    monkeypatch.setattr(OllamaAdapter, "models", lambda self: ["qwen2.5:1.5b"])
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py")
    app.session_state["page_navigation"] = "Benchmark Runner"
    app.session_state["benchmark_runtime"] = "Ollama (real)"
    app.session_state["ollama_model_select"] = "qwen2.5:1.5b"
    app.session_state["benchmark_prompt_categories"] = ["logic", "arithmetic", "extraction", "formatting"]
    app.session_state["benchmark_trial_count"] = 3
    app.session_state["benchmark_warmup_count"] = 1
    app.session_state["benchmark_max_tokens"] = 128
    app.session_state["benchmark_execution_mode"] = "single-user / sequential"
    app.run(timeout=20)

    assert not app.exception
    category_widget = next(widget for widget in app.multiselect if widget.key == "benchmark_prompt_categories")
    assert category_widget.key == "benchmark_prompt_categories"
    runtime_widget = next(widget for widget in app.selectbox if widget.key == "benchmark_runtime")
    assert "Ollama (real)" in runtime_widget.options
    assert "Demo (synthetic)" in runtime_widget.options
    assert runtime_widget.value == "Ollama (real)"
    model_widget = next(widget for widget in app.selectbox if widget.key == "ollama_model_select")
    assert model_widget.options == ["qwen2.5:1.5b"]
    assert model_widget.value == "qwen2.5:1.5b"
    assert any("Ollama API reachable" in element.value for element in app.success)
    assert category_widget.value == ["logic", "arithmetic", "extraction", "formatting"]
    assert next(widget for widget in app.number_input if widget.key == "benchmark_trial_count").value == 3
    assert next(widget for widget in app.number_input if widget.key == "benchmark_warmup_count").value == 1
    assert next(widget for widget in app.slider if widget.key == "benchmark_max_tokens").value == 128
    assert next(widget for widget in app.selectbox if widget.key == "benchmark_execution_mode").value == "single-user / sequential"
    run_button = next(widget for widget in app.button if widget.key == "benchmark_run_button")
    assert run_button.disabled is False
    assert OllamaAdapter.mode == "real"

    rendered = repr(app) + "\n" + "\n".join(str(element) for element in app.markdown)
    assert "DeltaGenerator" not in rendered
    assert "Creator of Delta protobuf messages." not in rendered
