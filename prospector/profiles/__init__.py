from pathlib import Path

AUTO_LOADED_PROFILES = list(
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
)
