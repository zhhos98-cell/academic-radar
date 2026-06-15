# Release Process

This project can publish a GitHub Release with Python package artifacts and a Windows desktop zip.

## What the release workflow builds

`Build Release` creates:

- Python source distribution, such as `academic_radar-0.2.0.tar.gz`.
- Python wheel, such as `academic_radar-0.2.0-py3-none-any.whl`.
- `AcademicRadar-Windows.zip`, containing `AcademicRadar.exe` and a short Windows README.

Before publishing, the workflow runs:

```bash
python scripts/validate_release.py
python -m unittest discover -s tests
```

## Publish from a tag

From a local git checkout:

```bash
git tag v0.2.0
git push origin v0.2.0
```

Pushing a `v*` tag starts the `Build Release` workflow. If the release does not already exist, the workflow creates it and attaches the artifacts.

## Publish manually from GitHub

1. Open the repository on GitHub.
2. Go to `Actions`.
3. Select `Build Release`.
4. Click `Run workflow`.
5. Enter a tag such as `v0.2.0`.
6. Wait for the workflow to finish.
7. Open `Releases` and confirm the assets are attached.

Manual publishing creates or updates a release for the requested tag using the current workflow commit as the target.

## Before publishing

Confirm these are true:

- `pyproject.toml` has the intended version.
- `docs/RELEASE.md` describes the intended release.
- `README.md` points users to the correct web builder and release flow.
- `python scripts/validate_release.py` passes.
- `python -m unittest discover -s tests` passes.
- No private runtime files, watchlists, OPML exports, state files, email addresses, or CFP records are staged for release.

## After publishing

Check the release page as a stranger:

1. Download the source archive.
2. Download `AcademicRadar-Windows.zip`.
3. Confirm `AcademicRadar.exe` starts on Windows.
4. Open the web builder at `https://zhhos98-cell.github.io/academic-radar/`.
5. Confirm the release notes do not contain personal data.
