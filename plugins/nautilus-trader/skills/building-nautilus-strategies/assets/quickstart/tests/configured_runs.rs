use std::{path::Path, process::Command};

fn run_config(name: &str) -> anyhow::Result<std::process::Output> {
    let manifest = Path::new(env!("CARGO_MANIFEST_DIR"));
    Ok(
        Command::new(env!("CARGO_BIN_EXE_nautilus-skill-quickstart"))
            .arg(manifest.join("configs").join(name))
            .output()?,
    )
}

#[test]
fn configured_fx_and_equity_runs_fill_their_configured_quantities() -> anyhow::Result<()> {
    for (name, expected) in [
        (
            "fx.json",
            "filled_quantity=2000 position_quantity=2000 position_side=Long",
        ),
        (
            "equity.json",
            "filled_quantity=7 position_quantity=7 position_side=Short",
        ),
    ] {
        let output = run_config(name)?;
        let stdout = String::from_utf8(output.stdout)?;
        let stderr = String::from_utf8(output.stderr)?;
        assert!(
            output.status.success(),
            "{name} failed with stderr: {stderr}\nstdout: {stdout}"
        );
        assert!(
            stdout.contains("inputs=5 quotes=4 signals=1 orders=1 positions=1"),
            "{name} did not complete the expected replay: {stdout}"
        );
        assert!(
            stdout.contains(expected),
            "{name} did not report its cached fill and position metrics: {stdout}"
        );
    }
    Ok(())
}

#[test]
fn invalid_quantity_configuration_fails_before_engine_start() -> anyhow::Result<()> {
    let output = run_config("invalid-zero-quantity.json")?;
    let stderr = String::from_utf8(output.stderr)?;
    assert!(
        !output.status.success(),
        "zero quantity configuration unexpectedly ran"
    );
    assert!(
        stderr.contains("entry.quantity must be positive"),
        "unexpected invalid configuration error: {stderr}"
    );
    Ok(())
}
