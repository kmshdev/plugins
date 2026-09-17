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
    use std::cell::RefCell;

    use nautilus_common::{
        cache::Cache,
        clock::{Clock, TestClock},
        component::Component,
        timer::{TimeEvent, TimeEventCallback},
    };
    use nautilus_core::DurationNanos;
    use nautilus_model::data::ensure_custom_data_json_registered;
    use nautilus_model::identifiers::TraderId;

    use super::*;

    #[test]
    fn registered_actor_timer_requires_explicit_dispatch() -> anyhow::Result<()> {
        let clock = Rc::new(RefCell::new(TestClock::new()));
        let cache = Rc::new(RefCell::new(Cache::default()));
        let mut actor = QuoteCounter::new(
            InstrumentId::from("AUD/USD.SIM"),
            Rc::new(Observations::default()),
        );
        actor.register(TraderId::from("TIMER-001"), clock.clone(), cache)?;
        let observed = Rc::new(Cell::new(0_u64));
        let callback_observed = observed.clone();
        let callback_clock = clock.clone();
        let callback: Rc<dyn Fn(TimeEvent)> = Rc::new(move |event| {
            assert_eq!(callback_clock.borrow().timestamp_ns(), event.ts_event);
            callback_observed.set(event.ts_event.as_u64());
        });
        actor.clock().set_timer_ns(
            "QUOTE-COUNTER-001.heartbeat",
            DurationNanos::from_secs(1),
            None,
            None,
            Some(TimeEventCallback::from(callback)),
            Some(false),
            Some(false),
        )?;
        let events = clock
            .borrow_mut()
            .advance_time(UnixNanos::from(1_000_000_000_u64), true);
        let handlers = clock.borrow().match_handlers(events);
        assert_eq!(observed.get(), 0);
        assert_eq!(handlers.len(), 1);
        for handler in handlers {
            handler.run();
        }
        assert_eq!(observed.get(), 1_000_000_000);
        actor.clock().cancel_timers();
        Ok(())
    }

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
