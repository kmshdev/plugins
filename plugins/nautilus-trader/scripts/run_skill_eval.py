#!/usr/bin/env python3
"""Run SkillEvaluator 0.2.1 on arbitrary self-contained skills, with restart receipts."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

EXCLUDED = {".git", ".venv", "node_modules", "target", "__pycache__", ".pytest_cache", "results"}
VERSION = "0.2.1"
DIMENSIONS = {"security", "skill_execution", "skill_efficiency", "accuracy",
              "goal_accuracy", "behavior_check"}
PATCHES = {
    "provider_config.py": (
        'if leaf.startswith("gpt-5") or leaf in _NO_CUSTOM_TEMPERATURE_MODEL_IDS:',
        'if leaf.startswith(("gpt-5", "gpt-6")) or leaf in _NO_CUSTOM_TEMPERATURE_MODEL_IDS:',
    ),
    "tier3/harbor/templates/eval.py": (
        'if leaf.startswith("gpt-5") or leaf == "claude-mythos-preview":',
        'if leaf.startswith(("gpt-5", "gpt-6")) or leaf == "claude-mythos-preview":',
    ),
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Skill directories, SKILL.md files or collections")
    parser.add_argument("--output-dir", required=True, type=Path, help="Dedicated private run directory")
    parser.add_argument("--env-file", type=Path, help="Trusted dotenv file; values override process inputs")
    parser.add_argument("--python", type=Path, help="Interpreter with SkillEvaluator installed")
    parser.add_argument("--tool-bin", type=Path, action="append", default=[], help="Additional scanner bin directory")
    parser.add_argument("--tiers", default="1,2,3", help="Comma-separated subset of 1,2,3")
    parser.add_argument("--dataset", default="working", help="working, acceptance, or skill-relative JSON path")
    parser.add_argument("--gateway", choices=("auto", "neon", "none"), default="auto")
    parser.add_argument("--agent-model", help="OpenCode provider/model; inferred for OpenAI-compatible grading")
    parser.add_argument("--agent-base-url", help="Agent-only SDK base; must share the grader's HTTPS origin")
    parser.add_argument("--n-concurrent", type=int, default=1)
    parser.add_argument("--timeout-multiplier", type=float, default=2.0)
    parser.add_argument("--command-timeout", type=float, default=0, help="Outer command seconds; 0 uses SDK limits")
    parser.add_argument("--execute", action="store_true", help="Run selected tiers, including paid model calls")
    parser.add_argument("--resume", action="store_true", help="Reuse this run only if inputs/configuration match")
    parser.add_argument("--retry-stage", action="append", default=[], help="Explicit stage ID to rerun on resume")
    return parser.parse_args()


def bootstrap(python: Path | None) -> None:
    if python is None and importlib.util.find_spec("skillevaluator") is not None:
        return
    if python is None:
        executable = shutil.which("skillevaluator")
        if executable:
            first = Path(executable).read_text().splitlines()[0]
            if first.startswith("#!/") and " " not in first[2:]:
                python = Path(first[2:])
    if python is None:
        raise ValueError("SkillEvaluator is missing; supply --python with its installed interpreter")
    # Do not resolve venv python symlinks: the venv path selects its dependencies.
    python = python.absolute()
    if str(python) != sys.executable:
        if not python.is_file():
            raise ValueError("The selected evaluator interpreter does not exist")
        os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])
    if importlib.util.find_spec("skillevaluator") is None:
        raise ValueError("The selected interpreter has no SkillEvaluator installation")


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def files(root: Path, excluded: set[str] = EXCLUDED) -> list[Path]:
    result = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in dirs + names:
            if name not in excluded and (base / name).is_symlink():
                raise ValueError(f"Symlinks are not staged: {base / name}")
        dirs[:] = sorted(name for name in dirs if name not in excluded)
        for name in sorted(names):
            if name.startswith(".env"):
                raise ValueError(f"Credential-like file must not be staged: {base / name}")
            result.append(base / name)
    return result


def tree_digest(root: Path, excluded: set[str] = EXCLUDED) -> str:
    return digest([(str(path.relative_to(root)), hashlib.sha256(path.read_bytes()).hexdigest())
                   for path in files(root, excluded)])


def discover(paths: list[Path]) -> list[Path]:
    found: set[Path] = set()
    for original in paths:
        root = original.resolve(strict=True)
        if root.is_file():
            if root.name != "SKILL.md":
                raise ValueError("File inputs must be SKILL.md")
            found.add(root.parent)
            continue
        if (root / "SKILL.md").is_file():
            if (root / "skills").is_dir():
                raise ValueError("Choose the skills/ collection or the explicit root SKILL.md, not both")
            found.add(root)
            continue
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(name for name in dirs if name not in EXCLUDED)
            if any((Path(directory) / name).is_symlink() for name in dirs):
                raise ValueError("Collection contains a directory symlink")
            if "SKILL.md" in names:
                found.add(Path(directory).resolve())
                dirs[:] = []
    if not found:
        raise ValueError("No SKILL.md found in the requested inputs")
    return sorted(found)


def skill_name(root: Path) -> str:
    import yaml
    text = (root / "SKILL.md").read_text()
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {root}")
    try:
        metadata = yaml.safe_load(match[1])
    except yaml.YAMLError:
        raise ValueError(f"Invalid YAML frontmatter: {root}") from None
    name = metadata.get("name") if isinstance(metadata, dict) else None
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"Skill needs a lowercase, path-safe frontmatter name: {root}")
    return name


def patch_source(text: str, old: str, new: str) -> str:
    if text.count(new) == 1 and old not in text:
        return text
    if text.count(old) != 1 or new in text:
        raise ValueError("Evaluator compatibility patch does not match; no files were patched globally")
    return text.replace(old, new, 1)


def prepare_vendor(destination: Path, source: Path) -> None:
    shutil.copytree(source, destination / "skillevaluator",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for relative, (old, new) in PATCHES.items():
        path = destination / "skillevaluator" / relative
        path.write_text(patch_source(path.read_text(), old, new))
    distribution = importlib.metadata.distribution("skillevaluator")
    for item in distribution.files or []:
        if ".dist-info/licenses/" in str(item):
            target = destination / "licenses" / Path(item).name
            target.parent.mkdir(exist_ok=True)
            shutil.copy2(distribution.locate_file(item), target)


def agent_base(base: str | None, gateway: str, override: str | None) -> str | None:
    parsed = urlsplit(base or "")
    hostname = (parsed.hostname or "").lower()
    neon = gateway == "neon" or (
        gateway == "auto" and hostname.endswith((".neon.tech", ".neon.com"))
    )
    if not neon and override is None:
        return None
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise ValueError("An agent base override requires a clean HTTPS grader origin")
    if override is not None:
        selected = urlsplit(override)
        if (selected.scheme, selected.netloc) != (parsed.scheme, parsed.netloc):
            raise ValueError("Refusing to forward the grader key to another agent origin")
        if selected.username or selected.password or selected.query or selected.fragment:
            raise ValueError("Agent SDK base cannot contain credentials, query or fragment")
        return override.rstrip("/")
    if parsed.path.rstrip("/") != "/v1":
        raise ValueError("The Neon profile expects the grader's /v1 SDK base")
    return urlunsplit((parsed.scheme, parsed.netloc, "/openai/v1", "", ""))


def stage_skill(source: Path, target: Path, dataset: str, tier3: bool, base: str | None) -> None:
    import yaml
    target.mkdir(parents=True)
    for path in files(source):
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    if not tier3:
        return
    relative = {"working": "evals/evals.json", "acceptance": "evals/acceptance.json"}.get(dataset, dataset)
    selected = (target / relative).resolve()
    if not selected.is_relative_to(target.resolve()):
        raise ValueError("Dataset must be inside the selected skill")
    if selected.is_file():
        content = selected.read_bytes()
        # Do not expose unused held-outs; preserve non-dataset JSON configuration.
        for path in (target / "evals").glob("*.json"):
            value = json.loads(path.read_text())
            if isinstance(value, dict) and isinstance(value.get("evals"), list):
                path.unlink()
        (target / "evals/evals.json").write_bytes(content)
    else:
        # Missing datasets remain a visible strict-validation failure, never auto-generated.
        if (target / "evals/evals.json").is_file():
            (target / "evals/evals.json").unlink()
    if base is None:
        return
    config_path = target / "evals/config.yml"
    alternate = target / "evals/config.yaml"
    if alternate.exists():
        if config_path.exists():
            raise ValueError("Both config.yml and config.yaml exist; resolve the ambiguity")
        config_path = alternate
    try:
        config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {"schema_version": 1}
    except yaml.YAMLError:
        raise ValueError("Invalid skill runtime configuration YAML") from None
    if not isinstance(config, dict):
        raise ValueError("Skill runtime configuration must be a mapping")
    harbor = config.setdefault("harbor", {})
    if not isinstance(harbor, dict):
        raise ValueError("harbor configuration must be a mapping")
    runtime = harbor.setdefault("runtime_env", {})
    if not isinstance(runtime, dict):
        raise ValueError("runtime_env configuration must be a mapping")
    inline = runtime.get("OPENCODE_CONFIG_CONTENT", "{}")
    if not isinstance(inline, str):
        raise ValueError("OPENCODE_CONFIG_CONTENT must be a JSON string")
    opencode = json.loads(inline)
    if not isinstance(opencode, dict):
        raise ValueError("OpenCode inline configuration must be an object")
    providers = opencode.setdefault("provider", {})
    if not isinstance(providers, dict):
        raise ValueError("OpenCode provider configuration must be an object")
    provider = providers.setdefault("openai", {})
    if not isinstance(provider, dict):
        raise ValueError("OpenCode openai configuration must be an object")
    if provider.get("npm") not in (None, "@ai-sdk/openai"):
        raise ValueError("Neon Responses needs OpenCode's native OpenAI SDK; conflicting npm override")
    options = provider.setdefault("options", {})
    if not isinstance(options, dict):
        raise ValueError("OpenCode provider options must be an object")
    options.update({"baseURL": base, "apiKey": "{env:OPENAI_API_KEY}"})
    runtime["OPENCODE_CONFIG_CONTENT"] = json.dumps(opencode)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))


def redact(text: str, environment: dict[str, str]) -> str:
    values = [value for key, value in environment.items()
              if re.search(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|MODEL|BASE_URL", key) and value]
    for value in sorted(set(values), key=len, reverse=True):
        text = text.replace(value, "[REDACTED]")
    return re.sub(r"https?://[^\s'\"\\]+", "[REDACTED_URL]", text)


def save(path: Path, value: object) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def terminate(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def command(argv: list[str], environment: dict[str, str], output: Path, timeout: float) -> dict:
    output.mkdir(parents=True)
    raw = output / "stdout.private"
    status = "finished"
    with raw.open("w") as stream:
        process = subprocess.Popen(argv, stdout=stream, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, env=environment,
                                   cwd=output, start_new_session=True)
        try:
            code = process.wait(timeout=timeout or None)
        except subprocess.TimeoutExpired:
            terminate(process)
            status, code = "timed_out", 124
        except KeyboardInterrupt:
            terminate(process)
            status, code = "interrupted", 130
    with raw.open(errors="replace") as source, (output / "command.log").open("w") as log:
        for line in source:
            log.write(redact(line, environment))
    raw.unlink()
    return {"status": status, "returncode": code, "output": str(output)}


def complete_tier3(result: dict, count: int) -> bool:
    agent = result.get("agents", {}).get("opencode", {})
    if not (
        count > 0
        and result.get("execution_status") == "succeeded"
        and result.get("report_status") == "complete"
        and result.get("expected_attempts") == result.get("scored_attempts") == count * 2
        and agent.get("execution_status") == "succeeded"
        and agent.get("num_trials_with") == agent.get("num_trials_without") == count
    ):
        return False
    if any(agent.get(key) for key in ("execution_errors", "agent_runtime_failures", "job_failures", "trial_failures")):
        return False
    for arm in ("with_skill", "without_skill"):
        scores = agent.get(arm, {})
        if not DIMENSIONS.issubset(scores):
            return False
        if any(isinstance(scores[key], bool) or not isinstance(scores[key], (int, float))
               or not math.isfinite(scores[key]) or not 0 <= scores[key] <= 1 for key in DIMENSIONS):
            return False
    return True


def behavior_report_complete(reports: Path, count: int) -> bool:
    # Harbor also writes per-trial result.json files deeper in this tree.
    results = list(reports.glob("*/*/result.json"))
    if len(results) != 1:
        return False
    try:
        value = json.loads(results[0].read_text())
    except json.JSONDecodeError:
        return False
    return isinstance(value, dict) and complete_tier3(value, count)


def stages(skills: dict[str, Path], tiers: set[str]) -> list[tuple[str, str, Path]]:
    result = []
    for name, path in sorted(skills.items()):
        if "1" in tiers:
            result.extend([(f"{name}/static", "static", path), (f"{name}/rubric", "rubric", path)])
        if "2" in tiers:
            result.append((f"{name}/context", "context", path))
        if "3" in tiers:
            result.extend([(f"{name}/strict", "strict", path), (f"{name}/behavior", "behavior", path)])
    if "2" in tiers and len(skills) > 1:
        parent = next(iter(skills.values())).parent
        result.extend([("collection/descriptions", "descriptions", parent),
                       ("collection/full-body", "full-body", parent)])
    return result


def evaluator_args(kind: str, path: Path, output: Path, model: str, agent_model: str,
                   args: argparse.Namespace) -> list[str]:
    reports = ["-r", "json,html", "-o", str(output / "reports")]
    common = [str(path)]
    commands = {
        "static": ["validate", *common, "--type", "skill", "--no-dedup", "--continue-on-failure", "--llm", *reports],
        "rubric": ["rubric-eval", *common, "--min-score", "70", *reports],
        "context": ["context-optimization-check", *common, "--threshold", "0.80", *reports],
        "descriptions": ["similarity-check", *common, "--type", "skill", "--threshold", "0.75", *reports],
        "full-body": ["similarity-check", *common, "--type", "skill", "--threshold", "0.75", "--full-body", *reports],
        "strict": ["tier3", "validate", *common, "--strict", "--json"],
        "behavior": [
            "tier3", "evaluate", *common, "--agents", "opencode", "--env-mode", "docker",
            "--skill-workspace-mode", "isolated", "--model", model, "--agent-model", f"opencode={agent_model}",
            "--n-attempts", "1", "--no-stop-on-pass", "--agent-runtime-preflight",
            "--n-concurrent", str(args.n_concurrent), "--timeout-multiplier", str(args.timeout_multiplier),
            "--results-dir", str(output / "reports"), "--progress", "plain", "--harbor-keep-jobs",
        ],
    }
    return [sys.executable, "-m", "skillevaluator.cli", *commands[kind]]


def docker_ready() -> bool:
    try:
        return subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=30, check=False,
        ).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def run(args: argparse.Namespace, environment: dict[str, str]) -> int:
    from skillevaluator.provider_config import resolve_embedding_provider, resolve_llm_provider

    tiers = set(args.tiers.split(","))
    if not tiers or not tiers.issubset({"1", "2", "3"}):
        raise ValueError("--tiers must be a subset of 1,2,3")
    if (args.n_concurrent < 1 or not math.isfinite(args.timeout_multiplier)
            or args.timeout_multiplier <= 0 or not math.isfinite(args.command_timeout)
            or args.command_timeout < 0):
        raise ValueError("Concurrency and time allowances must be finite positive values (outer timeout may be 0)")
    if args.retry_stage and not args.resume:
        raise ValueError("--retry-stage requires --resume")
    bins = [path.resolve(strict=True) for path in args.tool_bin]
    if any(not path.is_dir() for path in bins):
        raise ValueError("--tool-bin needs directories")
    environment["PATH"] = os.pathsep.join([*(str(path) for path in bins), environment.get("PATH", "")])
    tools = {
        name: environment.get(variable) or shutil.which(name, path=environment["PATH"])
        for name, variable in (("semgrep", "SKILLEVALUATOR_SEMGREP_PATH"),
                               ("skillspector", "SKILLEVALUATOR_SKILLSPECTOR_PATH"))
    }
    tools["gitleaks"] = shutil.which("gitleaks", path=environment["PATH"])
    missing_tools = [name for name, path in tools.items() if not path or not os.access(path, os.X_OK)]
    for name in ("semgrep", "skillspector"):
        if tools[name]:
            environment[f"SKILLEVALUATOR_{name.upper()}_PATH"] = tools[name]
    llm = resolve_llm_provider(environment)
    embedding = resolve_embedding_provider(environment) if "2" in tiers else None
    agent_model = args.agent_model or (
        f"openai/{llm.model.removeprefix('openai/')}" if llm.provider in {"openai", "openai-compatible"} else ""
    )
    if "3" in tiers and not agent_model:
        raise ValueError("This provider needs an explicit OpenCode --agent-model provider/model")
    base = agent_base(llm.base_url, args.gateway, args.agent_base_url) if "3" in tiers else None
    if base and not agent_model.startswith("openai/"):
        raise ValueError("The agent-only base override supports OpenCode's openai provider")
    if importlib.metadata.version("skillevaluator") != VERSION:
        raise ValueError("Only the reviewed SkillEvaluator 0.2.1 profile is supported; requalify upgrades explicitly")
    source = Path(importlib.util.find_spec("skillevaluator").submodule_search_locations[0])
    roots = discover(args.paths)
    named = [(skill_name(root), root) for root in roots]
    if len({name for name, _ in named}) != len(named):
        raise ValueError("Duplicate skill names would collide; select unique skills")
    output = args.output_dir.resolve()
    if any(output.is_relative_to(root) or root.is_relative_to(output) for root in roots):
        raise ValueError("Output and skill input trees must not contain one another")
    identities = {name: tree_digest(root) for name, root in named}
    spec = {
        "skills": identities, "tiers": sorted(tiers), "dataset": args.dataset,
        "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "evaluator": tree_digest(source, {"__pycache__"}), "version": VERSION,
        "harbor": importlib.metadata.version("harbor") if "3" in tiers else None,
        "provider_config": digest({
            "llm": [llm.provider, llm.model, llm.base_url],
            "embedding": [embedding.provider, embedding.model, embedding.base_url] if embedding else None,
            "agent": agent_model, "agent_base": base,
        }),
    }
    if args.output_dir.is_symlink():
        raise ValueError("Output cannot be a symlink")
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    if output.stat().st_mode & 0o077:
        raise ValueError("Run directory must be private (mode 0700); choose a new dedicated directory")
    with (output / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Another runner owns this output directory") from None
        state_path = output / "run.json"
        if args.resume:
            state = json.loads(state_path.read_text())
            if state.get("spec") != spec:
                raise ValueError("Inputs, runner, evaluator or provider configuration changed; use a new output directory")
            if tree_digest(output / "snapshot") != state["snapshot_digest"]:
                raise ValueError("Frozen snapshot changed; refusing resume")
            if tree_digest(output / "vendor", {"__pycache__"}) != state["vendor_digest"]:
                raise ValueError("Isolated evaluator changed; refusing resume")
        else:
            if any(path.name != ".lock" for path in output.iterdir()):
                raise ValueError("Run directory is not empty; use --resume or a new directory")
            prepare_vendor(output / "vendor", source)
            for name, root in named:
                stage_skill(root, output / "snapshot/skills" / name, args.dataset, "3" in tiers, base)
            if identities != {name: tree_digest(root) for name, root in named}:
                raise ValueError("Skill inputs changed during staging; use a new run directory")
            state = {"schema_version": 1, "spec": spec, "stages": {},
                     "snapshot_digest": tree_digest(output / "snapshot"),
                     "vendor_digest": tree_digest(output / "vendor", {"__pycache__"})}
        environment["PYTHONPATH"] = str(output / "vendor")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHON_DOTENV_DISABLED"] = "1"
        skills = {name: output / "snapshot/skills" / name for name in identities}
        planned = stages(skills, tiers)
        unknown = set(args.retry_stage) - {key for key, _, _ in planned}
        if unknown:
            raise ValueError("Unknown --retry-stage; use an ID from run.json")
        state["phase"] = "evaluation" if args.execute else "preflight"
        state["prerequisites"] = {
            "missing_scanners": missing_tools if "1" in tiers else [],
            "docker_available": docker_ready() if "3" in tiers else None,
        }
        save(state_path, state)
        failed = bool("1" in tiers and missing_tools) or (
            "3" in tiers and not state["prerequisites"]["docker_available"]
        )
        if "1" in tiers and missing_tools:
            print("Missing scanners: " + ", ".join(missing_tools) + "; use --tool-bin or restore prerequisites")
        if "3" in tiers and not state["prerequisites"]["docker_available"]:
            print("Docker unavailable; behavioral execution is blocked")
        for key, kind, path in planned:
            if not args.execute and kind != "strict":
                continue
            previous = state["stages"].get(key, [])
            if previous and key not in args.retry_stage:
                latest = previous[-1]
                if latest.get("status") == "finished":
                    for relative, expected in latest.get("artifacts", {}).items():
                        artifact = output / relative
                        if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest() != expected:
                            raise ValueError("A completed stage artifact changed or disappeared")
                    failed |= latest["returncode"] != 0
                    continue
                print(f"{key}: incomplete; explicit --retry-stage required")
                failed = True
                continue
            attempt_dir = output / "attempts" / key / f"{len(previous) + 1}-{time.time_ns()}"
            settings = {"n_concurrent": args.n_concurrent, "timeout_multiplier": args.timeout_multiplier,
                        "command_timeout": args.command_timeout}
            state["stages"].setdefault(key, []).append(
                {"status": "running", "returncode": None, "output": str(attempt_dir), "settings": settings}
            )
            save(state_path, state)
            if kind == "static" and missing_tools:
                record = {"status": "blocked", "returncode": 1, "reason": "Missing scanners"}
            elif kind == "behavior" and state["stages"].get(f"{path.name}/strict", [{}])[-1].get("returncode") != 0:
                record = {"status": "blocked", "returncode": 1, "reason": "strict validation"}
            elif kind == "behavior" and not state["prerequisites"]["docker_available"]:
                record = {"status": "blocked", "returncode": 1, "reason": "Docker daemon unavailable"}
            else:
                child_environment = environment.copy()
                if kind == "static" and llm.provider == "openai-compatible":
                    # Scope this guard to SkillSpector; native OpenAI embeddings keep their own key.
                    for variable in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_PROJECT_ID",
                                     "SKILLSPECTOR_PROVIDER", "SKILLSPECTOR_MODEL",
                                     "SKILLSPECTOR_COMPAT_API_KEY", "SKILLSPECTOR_COMPAT_BASE_URL"):
                        child_environment.pop(variable, None)
                record = command(evaluator_args(kind, path, attempt_dir, llm.model, agent_model, args),
                                 child_environment, attempt_dir, args.command_timeout)
                artifacts = list((attempt_dir / "reports").rglob("*.json"))
                if kind == "behavior" and record["status"] == "finished":
                    count = len(json.loads((path / "evals/evals.json").read_text())["evals"])
                    if not behavior_report_complete(attempt_dir / "reports", count):
                        record.update(status="incomplete", reason="Missing/incomplete paired report", returncode=1)
                elif kind != "strict" and record["status"] == "finished" and not artifacts:
                    record.update(status="incomplete", reason="No JSON report", returncode=1)
                log = attempt_dir / "command.log"
                record["artifacts"] = {
                    str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [*artifacts, log] if p.is_file()
                }
            record["settings"] = settings
            state["stages"][key][-1] = record
            save(state_path, state)
            print(f"{key}: {record['status']} (exit {record['returncode']})")
            failed |= record["returncode"] != 0 or record["status"] != "finished"
            if record["status"] == "interrupted":
                return 130
        state["status"] = "attention_required" if failed else (
            "commands_completed" if args.execute else "preflight_complete_not_evaluated"
        )
        save(state_path, state)
        print(f"Receipt: {state_path}")
        print("Raw evaluator artifacts are private; command success is not universal skill correctness.")
        return 1 if failed else 0


def main() -> int:
    args = arguments()
    os.umask(0o077)
    environment = os.environ.copy()
    try:
        bootstrap(args.python)
        from dotenv import dotenv_values
        if args.env_file:
            if not args.env_file.is_file():
                raise ValueError("The requested environment file does not exist")
            environment.update({
                key: value for key, value in dotenv_values(args.env_file, interpolate=False).items()
                if value is not None
            })
        return run(args, environment)
    except (OSError, ValueError, subprocess.SubprocessError, ModuleNotFoundError,
            importlib.metadata.PackageNotFoundError) as error:
        # Never print provider exceptions that could include an endpoint or credential.
        print(f"Runner stopped ({type(error).__name__}): {redact(str(error), environment)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
