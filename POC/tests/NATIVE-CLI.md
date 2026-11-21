# Running the native CLI suite

The test-only [run_codex_suite.py](run_codex_suite.py) uses Python's standard
library and the installed `codex` executable. It adds no Skilleto runtime,
MCP service or package dependency.

From this repository root in a normal terminal under the account that runs
Codex:

```powershell
python POC/tests/run_codex_suite.py prepare --lab-parent .test-lab
```

The command prints a new `lab_root` and `output_dir`. Use that exact output
directory for the run, for example:

```powershell
python POC/tests/run_codex_suite.py run --output POC/tests/runs/native-cli-YYYYMMDD-HHMMSS --workers 2 --timeout 180
```

To select cases, append `--cases p01-explicit-edit p21-no-task`, using names
from the manifest. Every `prepare` creates fresh projects and copies the
whole skill. The runner refuses to overwrite an existing case result.
The built-in suite defines 15 cases; the recorded run additionally contains
four supplemental projects for live captured evidence, recovery and install
preflight, followed by two activation probes sharing the installation project.
Those probes use recorded `project_directory` and optional `resume_session`
fields instead of creating more projects.

On Windows, create and run the lab under the **same user account**. Directories
owned by a nested sandbox account can prevent the native CLI's sandbox setup.
The harness uses inherited directory permissions; it does not change ACLs or
disable the child sandbox.

Native sessions use `workspace-write`, approval policy `never`, and
`--no-daemon`. Ordinary cases are ephemeral. P17 preserves a session for an
actual second turn and consequently leaves normal CLI session history.
User model/configuration is inherited without persistent configuration edits.

Each case records exact prompts/argument arrays, native stdout JSONL, stderr,
final response, session IDs, duration, exit/timeout information, tool events,
before/after hashes and copies of changed files. Execution status is **not**
an automatic behavioral grade. Inspect source-loading evidence and actual
artifacts using [scenarios.md](scenarios.md). A completed native turn can
coexist with a launcher timeout while waiting for process/pipes to close;
report both.

No built-in test authorizes third-party package execution or skill installation.
Live queries and P09 need their own actual user consent. The
[recorded results](results.md) separate these actions from local fixtures
and synthetic failure recovery. A bounded prior discovery consent must not
be reused for additional live queries or installation.
