#!/usr/bin/env python3
"""Validate local GitHub Action metadata and workflow YAML files."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by CI setup failures only.
    print(
        "PyYAML is required. Install it with: python3 -m pip install PyYAML==6.0.3",
        file=sys.stderr,
    )
    sys.exit(2)


ACTION_FILENAMES = {"action.yml", "action.yaml"}
WORKFLOW_SUFFIXES = {".yml", ".yaml"}


class ValidationError(Exception):
    """Raised when a file does not match the expected GitHub Actions shape."""


class UniqueKeyLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.load(handle, Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        raise ValidationError(f"{path}: invalid YAML: {error}") from error


def require_mapping(value: Any, path: Path, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: {field} must be a mapping")
    return value


def require_non_empty_string(value: Any, path: Path, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def validate_inputs(metadata: dict[str, Any], path: Path) -> None:
    inputs = metadata.get("inputs")
    if inputs is None:
        return

    require_mapping(inputs, path, "inputs")
    for input_name, input_metadata in inputs.items():
        if not isinstance(input_name, str) or not input_name.strip():
            raise ValidationError(f"{path}: input names must be non-empty strings")
        require_mapping(input_metadata, path, f"inputs.{input_name}")
        require_non_empty_string(input_metadata.get("description"), path, f"inputs.{input_name}.description")
        if "required" in input_metadata and not isinstance(input_metadata["required"], bool):
            raise ValidationError(f"{path}: inputs.{input_name}.required must be a boolean")


def validate_outputs(metadata: dict[str, Any], path: Path, using: str) -> None:
    outputs = metadata.get("outputs")
    if outputs is None:
        return

    require_mapping(outputs, path, "outputs")
    for output_name, output_metadata in outputs.items():
        if not isinstance(output_name, str) or not output_name.strip():
            raise ValidationError(f"{path}: output names must be non-empty strings")
        require_mapping(output_metadata, path, f"outputs.{output_name}")
        require_non_empty_string(output_metadata.get("description"), path, f"outputs.{output_name}.description")
        if using == "composite":
            require_non_empty_string(output_metadata.get("value"), path, f"outputs.{output_name}.value")


def validate_composite_steps(runs: dict[str, Any], path: Path) -> None:
    steps = runs.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValidationError(f"{path}: runs.steps must be a non-empty list for composite actions")

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValidationError(f"{path}: runs.steps[{index}] must be a mapping")

        has_uses = isinstance(step.get("uses"), str) and bool(step["uses"].strip())
        has_run = isinstance(step.get("run"), str) and bool(step["run"].strip())
        if has_uses == has_run:
            raise ValidationError(f"{path}: runs.steps[{index}] must define exactly one of uses or run")


def validate_runs(metadata: dict[str, Any], path: Path) -> str:
    runs = require_mapping(metadata.get("runs"), path, "runs")
    using = require_non_empty_string(runs.get("using"), path, "runs.using").lower()

    if using == "composite":
        validate_composite_steps(runs, path)
    elif using.startswith("node"):
        require_non_empty_string(runs.get("main"), path, "runs.main")
    elif using == "docker":
        require_non_empty_string(runs.get("image"), path, "runs.image")
    else:
        raise ValidationError(f"{path}: runs.using has unsupported value {using!r}")

    return using


def validate_action_metadata(path: Path) -> None:
    metadata = require_mapping(load_yaml(path), path, "action metadata")
    require_non_empty_string(metadata.get("name"), path, "name")
    require_non_empty_string(metadata.get("description"), path, "description")
    using = validate_runs(metadata, path)
    validate_inputs(metadata, path)
    validate_outputs(metadata, path, using)


def action_metadata_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name in ACTION_FILENAMES and ".git" not in path.parts
    )


def workflow_files(root: Path) -> list[Path]:
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return []
    return sorted(
        path
        for path in workflows_dir.rglob("*")
        if path.is_file() and path.suffix in WORKFLOW_SUFFIXES
    )


def main() -> int:
    root = Path.cwd()
    errors: list[str] = []

    actions = action_metadata_files(root)
    if not actions:
        errors.append("No action.yml or action.yaml files were found")
    for path in actions:
        try:
            validate_action_metadata(path)
            print(f"OK action metadata: {path}")
        except ValidationError as error:
            errors.append(str(error))

    for path in workflow_files(root):
        try:
            load_yaml(path)
            print(f"OK workflow YAML: {path}")
        except ValidationError as error:
            errors.append(str(error))

    if errors:
        print("\nValidation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(actions)} action metadata file(s) and {len(workflow_files(root))} workflow file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
