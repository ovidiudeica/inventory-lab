from scripts.check_secrets import findings


def test_credential_patterns_without_real_keys():
    fake = "sk-" + "ant-" + "x" * 32
    assert list(findings("example: " + fake))[0][0] == "Anthropic API key"
    assert list(findings("ANTHROPIC_API_KEY=")) == []
    assert list(findings("ANTHROPIC_API_KEY=" + "dummy-value"))[0][0] == "Non-empty AI key assignment"
