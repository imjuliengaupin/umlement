from pathlib import Path


def test_additional_demo_projects_exist() -> None:
    base = Path(__file__).resolve().parents[1]
    assert (base / "demo_space_cafe").is_dir()
    assert (base / "demo_mech_pet").is_dir()
