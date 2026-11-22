from pathlib import Path

AUTO_LOADED_PROFILES = [
    Path(*parts)
    for parts in (
        (".landscape.yml",),
        (".landscape.yaml",),
        ("landscape.yml",),
        ("landscape.yaml",),
        (".prospector.yaml",),
        (".prospector.yml",),
        ("prospector.yaml",),
        ("prospector.yml",),
        ("prospector", ".prospector.yaml"),
        ("prospector", ".prospector.yml"),
        ("prospector", "prospector.yaml"),
        ("prospector", "prospector.yml"),
        (".prospector", ".prospector.yaml"),
        (".prospector", ".prospector.yml"),
        (".prospector", "prospector.yaml"),
        (".prospector", "prospector.yml"),
    )
]

# Only used when it contains a [tool.prospector] table, and after all of the above
PYPROJECT_PROFILE = Path("pyproject.toml")
