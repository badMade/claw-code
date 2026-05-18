with open(".github/workflows/auto-merge.yml", "r") as f:
    content = f.read()

# Replace the incomplete script block with the corrected version
corrected_script = """            const pr = context.payload.pull_request;
            const owner = context.repo.owner;
            const repo = context.repo.repo;

            // Wait up to 5 minutes for checks to complete
            for (let i = 0; i < 10; i++) {
              await new Promise(r => setTimeout(r, 30000));

              const { data: checkRuns } = await github.rest.checks.listForRef({
                owner, repo,
                ref: pr.head.sha
              });

              // Only consider check runs from GitHub Actions (or relevant apps)
              // Ignore the auto-merge check run itself if possible
              const relevantChecks = checkRuns.check_runs.filter(cr => cr.name !== 'auto-merge');

              const allCompleted = relevantChecks.every(cr => cr.status === 'completed');
              if (allCompleted) {
                const allSuccess = relevantChecks.every(cr => cr.conclusion === 'success' || cr.conclusion === 'skipped' || cr.conclusion === 'neutral');
                if (!allSuccess) {
                  core.setFailed('Some CI checks failed.');
                  return;
                }
                break; // All passed
              }
            }"""

if "const { data: checkRuns } = await github.rest.checks.listForRef({\n                owner, repo,\n" in content:
    # Let's just rewrite it completely because it's truncated at the end
    pass
