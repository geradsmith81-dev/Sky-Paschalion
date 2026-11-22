# Sky Paschalion · Πασχάλιον

The Christian calendars of the churches of the ancient apostolic sees — Catholic (Latin and Eastern Catholic),
Eastern Orthodox, Oriental Orthodox and the Church of the East — with Pascha by the Western, Eastern and
astronomical rules, the feasts and fasts of 55 churches, the hours of prayer set by the Sun, the Moon, and a live
*Face east* compass, from NASA JPL DE440s astronomy. A Streamlit app in the Sky series with Sky Luach, Sky Taqwim
and Sky Gahshomar. How it works: [HOW_IT_WORKS.md](HOW_IT_WORKS.md). Checks: [VALIDATION.md](VALIDATION.md).
Sources: [SOURCES.md](SOURCES.md).

## On a Windows computer (desktop bundle)

1. Install Python 3.12 or newer from https://www.python.org/downloads/ and tick **Add python.exe to PATH**.
2. Unzip `SkyPaschalion_desktop.zip` to a folder of your choice (for example `C:\SkyPaschalionApp`).
3. Double-click **Start app.bat**. The first start opens a setup window that creates a private Python environment
   in the folder (`.venv`) and installs the exact, checksum-verified components listed in `requirements.txt`; it
   needs the internet and takes 2–5 minutes, and puts a **Sky Paschalion** icon on the Desktop and in the Start
   menu (if it is missing, double-click **Create desktop icon.bat**). The app then opens in its own Microsoft Edge
   window at **http://localhost:8514** (port 8514, so it can run next to Sky Luach 8505, Sky Taqwim 8511 and
   Sky Gahshomar 8513). There is no console window: close the app window and the app stops about a minute and a
   half later, or press **Quit Sky Paschalion** at the bottom of the page.
4. To open this computer's copy on a phone or another computer on the same network, double-click
   **Share on this network.bat**; its window shows the address and a new password each time. See
   `READ ME FIRST.txt` for details, where the app keeps its logs (`%LOCALAPPDATA%\SkyPaschalion`) and how to check
   a download against `SHA256SUMS.txt`.

After an update of the app (a new `requirements.txt`), Start app.bat installs the changed components by itself in
the setup window. The desktop bundle
includes the JPL ephemeris (`ephem/de440s.bsp`), so the app works offline after the first setup.

## On the web and on phones (GitHub + Streamlit Community Cloud)

Use `SkyPaschalion_app.zip` (the same app without the 32 MB ephemeris; the app downloads `de440s.bsp` from JPL
the first time it starts).

1. On GitHub press **New repository**, name it `sky-paschalion`, choose **Public**, and create it.
2. Press **Add file → Upload files** and drag in **everything** from the unzipped `sky-paschalion` folder (drag the
   folders themselves so `assets/`, `tools/`, `tests/` and `ephem/` keep their contents). Commit.
3. GitHub's web upload can drop folders whose names begin with a dot. If `.streamlit/config.toml` is missing in
   the repository, press **Add file → Create new file**, type the name `.streamlit/config.toml`, paste the text of
   `config.toml for GitHub (paste).txt`, and commit. (Without it the app is still readable: `theme.py` forces the
   colours.)
4. Go to https://share.streamlit.io, press **Create app**, choose the repository `sky-paschalion`, branch `main`,
   main file `app.py`, and under **App URL** choose a custom address such as `sky-paschalion` →
   **https://sky-paschalion.streamlit.app/**. Press **Deploy**. (The address can also be set later under the app's
   **⋮ → Settings → General → App URL**; the old address does not redirect.)
5. Phone icon: publish `sky-paschalion-launcher.zip` on GitHub Pages as described in its README, then set
   `APP_URL` in the launcher's `index.html` to the app's address and bump the cache name in `sw.js`
   (`sky-paschalion-launcher-v1` → `v2`) so phones fetch the new copy.

## Files

| File or folder | What it is |
|---|---|
| `app.py` | Settings (church, calendar, Paschalion, language, hours, place), navigation and the context for the pages. |
| `pages.py` | The pages: Today, Month, Year, Feasts & fasts, Paschalion, Hours, Compare, Traditions, How it works, About. |
| `liturgy.py` | Applies the calendar and Paschalion settings to the feast tables; seasons; date formatting. |
| `calendars.py`, `paschalion.py`, `sky_layer.py`, `sky_engine.py` | The engine: six calendars, three Paschalion rules, Sun, hours and Moon from JPL DE440s. |
| `sects.py`, `feasts.py`, `names.py` | The churches, their feasts and fasts, and the names in the liturgical languages. |
| `theme.py`, `ornaments.py`, `assets/` | Colours, fonts (OFL), the Chi-Rho emblem, crosses and mosaic bands. |
| `orient_live.py`, `locator.py`, `device.py`, `places.py` | The live compass, the device location, the phone layout and the place search. |
| `tools/` | `apptest_sweep.py` (headless test of every page), `js_check.py` (compass JavaScript), `render_previews.py`, `validate.py` (engine validation); in the Windows desktop bundle also `launch.py` (the windowless launcher). |
| `tests/` | Unit tests of the engine and the content (`tests/_stub` is used by the content tests only). |

## Tests

From the app folder, with the packages of `requirements-validation.txt`:
`python tools/apptest_sweep.py` (275 runs, 0 exceptions when this bundle was built),
`python tools/js_check.py` (33 / 33), `python tools/validate.py` (writes `tools/validation_results.json`).

## License

Sky Paschalion is released under the MIT License — Copyright (c) 2026 Gerad Smith. See [LICENSE](LICENSE).
The bundled fonts (SIL Open Font License 1.1), the JPL ephemeris and the World Magnetic Model (US government
works), GeoNames place data (CC BY 4.0) and the other third-party material keep their own licences: see
[THIRD_PARTY.md](THIRD_PARTY.md).

## Run locally

Install the exact, checksum-verified versions the app was tested with (Python 3.12 or newer):

```
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes --only-binary ":all:" -r requirements.txt
.venv\Scripts\python -m streamlit run app.py --server.address 127.0.0.1
```

`requirements.in` lists the direct components; `requirements.txt` is the full lock with SHA-256
hashes (generated with `uv pip compile requirements.in --universal --python-version 3.12
--generate-hashes --only-binary :all:`). The same lock serves Streamlit Community Cloud.

## Security and privacy

- The Windows desktop copy of Sky Paschalion listens on this computer only (127.0.0.1). "Share on this network.bat" can open it to the local network, protected by a new password each time; only the person at the computer sees the Quit button.
- The desktop copy keeps its data and logs in `%LOCALAPPDATA%\SkyPaschalion`, checks its program files against `MANIFEST.sha256` at every start, and each release publishes SHA-256 checksums of its zips in `SHA256SUMS.txt`.
- All components are pinned to exact versions and installed with `--require-hashes`.
- The desktop-only code (`desktop.py`) does nothing on a hosted copy: no Quit button is shown there.
- Sky Paschalion stores nothing about you: your place and settings live only in the open browser session. The desktop copy downloads the JPL ephemeris to `%LOCALAPPDATA%\SkyPaschalion\ephem` only if the bundled copy is missing.
