class CraftHarness < Formula
  desc "Multi-runtime agent harness for agents, skills, orchestration, and verification"
  homepage "https://github.com/woogi-kang/craft-harness"
  url "https://github.com/woogi-kang/craft-harness.git", branch: "main"
  version "0.1.0"
  license "Apache-2.0"

  depends_on "python@3.13"

  def install
    libexec.install Dir["*"]

    (bin/"craft").write <<~EOS
      #!/usr/bin/env bash
      set -euo pipefail
      export CRAFT_HARNESS_ROOT="#{libexec}"
      export CRAFT_HARNESS_CALLER_CWD="${CRAFT_HARNESS_CALLER_CWD:-$(pwd)}"
      export PYTHONPATH="#{libexec}/src${PYTHONPATH:+:$PYTHONPATH}"
      exec "#{Formula["python@3.13"].opt_bin}/python3" -m craft_harness.cli "$@"
    EOS
    chmod 0755, bin/"craft"
  end

  test do
    assert_match "Craft Harness Doctor", shell_output("#{bin}/craft doctor")
    assert_match "OK: skills", shell_output("#{bin}/craft validate")
  end
end
