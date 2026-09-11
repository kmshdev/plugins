use std::{cell::Cell, rc::Rc, sync::Arc};

use nautilus_common::{
    actor::{DataActor, DataActorConfig, DataActorCore},
    nautilus_actor,
};
use nautilus_core::UnixNanos;
use nautilus_model::{
    data::{CustomData, CustomDataTrait, DataType, QuoteTick},
    identifiers::{ActorId, InstrumentId},
};
use nautilus_persistence_macros::custom_data;

#[custom_data(no_arrow)]
pub struct SignalV1 {
    pub value: i64,
    pub ts_event: UnixNanos,
    pub ts_init: UnixNanos,
}

pub fn signal_type() -> DataType {
    DataType::new(SignalV1::type_name_static(), None, None)
}

pub fn signal(value: i64, ts_event: UnixNanos, ts_init: UnixNanos) -> CustomData {
    CustomData::new(
        Arc::new(SignalV1::new(value, ts_event, ts_init)),
        signal_type(),
    )
}

#[derive(Debug, Default)]
pub struct Observations {
    pub quotes: Cell<u64>,
    pub signals: Cell<u64>,
}

#[derive(Debug)]
pub struct QuoteCounter {
    core: DataActorCore,
    instrument_id: InstrumentId,
    observations: Rc<Observations>,
}

impl QuoteCounter {
    pub fn new(instrument_id: InstrumentId, observations: Rc<Observations>) -> Self {
        Self {
            core: DataActorCore::new(DataActorConfig {
                actor_id: Some(ActorId::from("QUOTE-COUNTER-001")),
                ..Default::default()
            }),
            instrument_id,
            observations,
        }
    }

    fn subscribe(&mut self) {
        self.subscribe_quotes(self.instrument_id, None, None);
        self.subscribe_data(signal_type(), None, None);
    }
}

nautilus_actor!(QuoteCounter);

impl DataActor for QuoteCounter {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.cache().try_instrument(&self.instrument_id)?;
        self.subscribe();
        Ok(())
    }

    fn on_resume(&mut self) -> anyhow::Result<()> {
        self.subscribe();
        Ok(())
    }

    fn on_stop(&mut self) -> anyhow::Result<()> {
        self.unsubscribe_quotes(self.instrument_id, None, None);
        self.unsubscribe_data(signal_type(), None, None);
        Ok(())
    }

    fn on_reset(&mut self) -> anyhow::Result<()> {
        self.observations.quotes.set(0);
        self.observations.signals.set(0);
        Ok(())
    }

    fn on_quote(&mut self, _quote: &QuoteTick) -> anyhow::Result<()> {
        let count = self.observations.quotes.get();
        self.observations.quotes.set(
            count
                .checked_add(1)
                .ok_or_else(|| anyhow::anyhow!("Quote count overflow"))?,
        );
        Ok(())
    }

    fn on_data(&mut self, data: &CustomData) -> anyhow::Result<()> {
        let payload = data
            .data
            .as_any()
            .downcast_ref::<SignalV1>()
            .ok_or_else(|| anyhow::anyhow!("Expected SignalV1"))?;
        anyhow::ensure!(payload.ts_event <= payload.ts_init, "Noncausal signal");
        let count = self.observations.signals.get();
        self.observations.signals.set(
            count
                .checked_add(1)
                .ok_or_else(|| anyhow::anyhow!("Signal count overflow"))?,
        );
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use nautilus_model::data::ensure_custom_data_json_registered;

    use super::*;

    #[test]
    fn json_preserves_signal_identity_and_time() -> anyhow::Result<()> {
        ensure_custom_data_json_registered::<SignalV1>()?;
        let original = signal(7, 100_u64.into(), 110_u64.into());
        let restored = CustomData::from_json_bytes(&serde_json::to_vec(&original)?)?;
        let payload = restored
            .data
            .as_any()
            .downcast_ref::<SignalV1>()
            .ok_or_else(|| anyhow::anyhow!("Wrong restored payload"))?;
        assert_eq!(payload.value, 7);
        assert_eq!(payload.ts_event, UnixNanos::from(100_u64));
        assert_eq!(payload.ts_init, UnixNanos::from(110_u64));
        assert_eq!(restored.data_type, signal_type());
        Ok(())
    }
}
