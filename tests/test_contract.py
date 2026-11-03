from __future__ import annotations

import importlib.resources

import stripcontrol

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "STANDARD_WHITESPACE",
    "UNICODE_VERSION",
    "ControlStripper",
    "escape_control",
    "find_control",
    "has_control",
    "strip_control",
    "strip_control_bytes",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(stripcontrol.__all__) == sorted(PUBLIC_API)


def test_public_namespace_contains_only_documented_exports() -> None:
    assert {name for name in vars(stripcontrol) if not name.startswith("_")} == set(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in stripcontrol.__all__:
        assert hasattr(stripcontrol, name)


def test_version_is_a_three_part_string() -> None:
    parts = stripcontrol.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("stripcontrol").joinpath("py.typed").is_file()
