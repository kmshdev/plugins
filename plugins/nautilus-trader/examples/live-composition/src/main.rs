use std::path::PathBuf;

use nautilus_common::enums::Environment;
use nautilus_databento::{data::DatabentoDataClientConfig, factories::DatabentoDataClientFactory};
use nautilus_interactive_brokers::{
    config::InteractiveBrokersExecutionClientConfig,
    factories::InteractiveBrokersExecutionClientFactory,
};
use nautilus_live::{
    config::{LiveRiskEngineConfig, RoutingConfig},
    node::LiveNode,
};
use nautilus_model::identifiers::TraderId;

const PLACEHOLDER_DATABENTO_KEY: &str = "00000000000000000000000000000000";
const PLACEHOLDER_IBKR_ACCOUNT: &str = "DU000000";

fn main() -> anyhow::Result<()> {
    let publishers_path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("publishers.json");
    let data = DatabentoDataClientConfig::new(
        PLACEHOLDER_DATABENTO_KEY.to_string(),
        publishers_path,
        true,
        true,
    );
    let execution = InteractiveBrokersExecutionClientConfig {
        account_id: Some(PLACEHOLDER_IBKR_ACCOUNT.to_string()),
        ..Default::default()
    };
    let routing = RoutingConfig::builder().default(true).build();

    let mut node = LiveNode::builder(TraderId::from("LIVE-COMPOSITION-001"), Environment::Live)?
        .with_reconciliation(true)
        .with_risk_engine_config(LiveRiskEngineConfig {
            bypass: false,
            ..Default::default()
        })
        .add_data_client_with_routing(
            None,
            Box::new(DatabentoDataClientFactory::new()),
            Box::new(data),
            routing.clone(),
        )?
        .add_exec_client_with_routing(
            None,
            Box::new(InteractiveBrokersExecutionClientFactory::new()),
            Box::new(execution),
            routing,
        )?
        .build()?;

    node.dispose();
    println!("live-node construction complete; no clients started");
    Ok(())
}
