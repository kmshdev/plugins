CREATE SCHEMA IF NOT EXISTS run_control;

CREATE TABLE IF NOT EXISTS run_control.runs (
    run_id UUID NOT NULL,
    attempt_id UUID NOT NULL,
    instance_id UUID NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('backtest', 'sandbox', 'live')),
    state TEXT NOT NULL CHECK (state IN ('planned', 'running', 'completed', 'failed', 'incomplete')),
    image_digest TEXT NOT NULL,
    config_digest TEXT NOT NULL,
    artifact_prefix TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    outcome JSONB,
    PRIMARY KEY (run_id, attempt_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS one_running_attempt_per_run
    ON run_control.runs (run_id) WHERE state = 'running';
