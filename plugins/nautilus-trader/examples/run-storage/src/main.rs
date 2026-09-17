use std::{
    cell::RefCell,
    path::{Path, PathBuf},
    rc::Rc,
};

use nautilus_backtest::config::BacktestEngineConfig;
use nautilus_common::{
    cache::{CacheConfig, database::CacheDatabaseFactory},
    enums::Environment,
    msgbus::{self, switchboard},
};
use nautilus_core::UUID4;
use nautilus_infrastructure::{redis::cache::RedisCacheConfig, sql::cache::PostgresCacheConfig};
use nautilus_live::node::LiveNode;
use nautilus_model::{
    data::QuoteTick,
    identifiers::{InstrumentId, TraderId},
    types::{Price, Quantity},
};
use nautilus_persistence::backend::{
    catalog::ParquetDataCatalog,
    feather::{FeatherWriter, RotationConfig as WriterRotationConfig},
};
use nautilus_system::config::{RotationConfig, StreamingConfig};

fn round_trip(root: &Path) -> anyhow::Result<(UUID4, PathBuf)> {
    let instance_id = UUID4::new();
    let directory = root.join(instance_id.to_string());
    std::fs::create_dir_all(&directory)?;
    let streaming = StreamingConfig::new(
        directory.to_string_lossy().into_owned(),
        "file".to_owned(),
        1000,
        false,
        RotationConfig::NoRotation,
    );
    streaming.validate()?;
    let backtest_config = BacktestEngineConfig {
        streaming: Some(streaming.clone()),
        instance_id: Some(instance_id),
        ..Default::default()
    };
    anyhow::ensure!(backtest_config.streaming.is_some());
    let _postgres_factory: Box<dyn CacheDatabaseFactory> = Box::new(PostgresCacheConfig::default());
    let mut node = LiveNode::builder(TraderId::from("STORAGE-PROBE-001"), Environment::Sandbox)?
        .with_instance_id(instance_id)
        .with_cache_config(CacheConfig {
            use_instance_id: true,
            flush_on_start: false,
            ..Default::default()
        })
        .with_cache_database_factory(Box::new(RedisCacheConfig {
            number_of_retries: 0,
            ..Default::default()
        }))
        .build()?;
    let writer = Rc::new(RefCell::new(FeatherWriter::from_uri(
        &directory
            .join("sandbox")
            .join(instance_id.to_string())
            .to_string_lossy(),
        None,
        node.kernel().clock(),
        WriterRotationConfig::NoRotation,
        None,
        Some(streaming.flush_interval_ms),
        false,
    )?));
    let subscriptions = FeatherWriter::subscribe_builtin_to_message_bus(Rc::clone(&writer))
        .map_err(|error| anyhow::anyhow!(error.to_string()))?;
    let quote = QuoteTick::new(
        InstrumentId::from("AUD/USD.SIM"),
        Price::new(0.65, 5),
        Price::new(0.6502, 5),
        Quantity::new(1000.0, 0),
        Quantity::new(1000.0, 0),
        1_000_000_000.into(),
        1_000_000_001.into(),
    );
    msgbus::publish_quote(switchboard::get_quotes_topic(quote.instrument_id), &quote);
    FeatherWriter::unsubscribe_from_message_bus(&subscriptions);
    let flush_result = nautilus_common::live::get_runtime()
        .block_on(writer.borrow_mut().close())
        .map_err(|error| anyhow::anyhow!(error.to_string()));
    node.dispose();
    flush_result?;
    let mut catalog =
        ParquetDataCatalog::from_uri(&directory.to_string_lossy(), None, None, None, None)?;
    catalog.convert_stream_to_data(
        &instance_id.to_string(),
        "quotes",
        Some("sandbox"),
        None,
        false,
    )?;
    let recovered = catalog.query_typed_data::<QuoteTick>(None, None, None, None, None, false)?;
    anyhow::ensure!(
        recovered == vec![quote],
        "Feather/Parquet round trip changed the quote"
    );
    Ok((instance_id, directory))
}

fn main() -> anyhow::Result<()> {
    let root = std::env::args_os()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| std::env::temp_dir().join("nautilus-run-storage"));
    anyhow::ensure!(
        !root.to_string_lossy().contains("://"),
        "This smoke test accepts only local filesystem paths"
    );
    let (instance_id, directory) = round_trip(&root)?;
    println!(
        "instance_id={instance_id} rows=1 feather_to_parquet=verified datafusion_readback=verified"
    );
    println!(
        "artifacts={} no_node_start=true no_database_connections=true",
        directory.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn builtin_writer_subscriber_rejects_async_callback_context() -> anyhow::Result<()> {
        let directory = tempfile::tempdir()?;
        let mut node = super::LiveNode::builder(
            super::TraderId::from("ASYNC-PROBE-001"),
            super::Environment::Sandbox,
        )?
        .build()?;
        let writer = super::Rc::new(super::RefCell::new(super::FeatherWriter::from_uri(
            &directory.path().to_string_lossy(),
            None,
            node.kernel().clock(),
            super::WriterRotationConfig::NoRotation,
            None,
            Some(1000),
            false,
        )?));
        let subscriptions =
            super::FeatherWriter::subscribe_builtin_to_message_bus(super::Rc::clone(&writer))
                .map_err(|error| anyhow::anyhow!(error.to_string()))?;
        let quote = super::QuoteTick::new(
            super::InstrumentId::from("AUD/USD.SIM"),
            super::Price::new(0.65, 5),
            super::Price::new(0.6502, 5),
            super::Quantity::new(1.0, 0),
            super::Quantity::new(1.0, 0),
            1.into(),
            2.into(),
        );
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            nautilus_common::live::get_runtime().block_on(async {
                super::msgbus::publish_quote(
                    super::switchboard::get_quotes_topic(quote.instrument_id),
                    &quote,
                );
            });
        }));
        super::FeatherWriter::unsubscribe_from_message_bus(&subscriptions);
        let closed = nautilus_common::live::get_runtime()
            .block_on(writer.borrow_mut().close())
            .map_err(|error| anyhow::anyhow!(error.to_string()));
        node.dispose();
        closed?;
        let panic =
            result.expect_err("0.64 built-in subscriber must not be used in an async callback");
        let message = panic
            .downcast_ref::<String>()
            .map(String::as_str)
            .or_else(|| panic.downcast_ref::<&str>().copied())
            .unwrap_or("");
        assert!(
            message.contains("Cannot start a runtime from within a runtime"),
            "{message}"
        );
        Ok(())
    }

    #[test]
    fn live_kernel_streaming_config_is_not_silently_accepted() -> anyhow::Result<()> {
        let builder = super::LiveNode::builder(
            super::TraderId::from("CONFIG-PROBE-001"),
            super::Environment::Sandbox,
        )?
        .with_streaming_config(super::StreamingConfig::new(
            "unused".to_owned(),
            "file".to_owned(),
            1000,
            false,
            super::RotationConfig::NoRotation,
        ));
        let error = builder
            .build()
            .err()
            .expect("0.64 must reject unsupported live streaming config");
        assert!(error.to_string().contains("streaming is not supported"));
        Ok(())
    }

    #[test]
    fn native_stream_converts_to_parquet_with_exact_identity_and_timestamps() -> anyhow::Result<()>
    {
        let directory = tempfile::tempdir()?;
        super::round_trip(directory.path())?;
        Ok(())
    }
}
