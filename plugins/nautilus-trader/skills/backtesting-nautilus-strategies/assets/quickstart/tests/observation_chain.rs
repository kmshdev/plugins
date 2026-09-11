use std::{cell::RefCell, rc::Rc};

use nautilus_backtest::{
    config::{BacktestEngineConfig, SimulatedVenueConfig},
    engine::BacktestEngine,
};
use nautilus_common::{
    actor::{DataActor, DataActorConfig, DataActorCore},
    nautilus_actor,
};
use nautilus_core::UnixNanos;
use nautilus_model::{
    data::{CustomData, Data, QuoteTick},
    enums::{AccountType, BookType, OmsType},
    identifiers::{ActorId, InstrumentId, StrategyId, Symbol, Venue},
    instruments::{CurrencyPair, Instrument, InstrumentAny},
    types::{Currency, Money, Price, Quantity},
};
use nautilus_skill_quickstart::{SignalV1, signal, signal_type};
use nautilus_trading::{
    nautilus_strategy,
    strategy::{StrategyConfig, StrategyCore},
};

#[derive(Debug)]
struct QuotePublisher {
    core: DataActorCore,
    instrument_id: InstrumentId,
    sequence: i64,
}

nautilus_actor!(QuotePublisher);

impl DataActor for QuotePublisher {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.cache().try_instrument(&self.instrument_id)?;
        self.subscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_stop(&mut self) -> anyhow::Result<()> {
        self.unsubscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_quote(&mut self, quote: &QuoteTick) -> anyhow::Result<()> {
        self.sequence = self
            .sequence
            .checked_add(1)
            .ok_or_else(|| anyhow::anyhow!("Sequence overflow"))?;
        let available_at = self.clock().timestamp_ns();
        anyhow::ensure!(available_at >= quote.ts_init, "Publication predates input");
        let observation = signal(self.sequence, quote.ts_event, available_at);
        // This producer never subscribes to its own synchronous publication.
        self.publish_data(&observation.data_type, &observation);
        Ok(())
    }
}

type Received = Rc<RefCell<Vec<(i64, UnixNanos, UnixNanos)>>>;

#[derive(Debug)]
struct ObservationConsumer {
    core: StrategyCore,
    received: Received,
}

nautilus_strategy!(ObservationConsumer);

impl DataActor for ObservationConsumer {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.subscribe_data(signal_type(), None, None);
        Ok(())
    }

    fn on_stop(&mut self) -> anyhow::Result<()> {
        self.unsubscribe_data(signal_type(), None, None);
        Ok(())
    }

    fn on_data(&mut self, data: &CustomData) -> anyhow::Result<()> {
        let payload = data
            .data
            .as_any()
            .downcast_ref::<SignalV1>()
            .ok_or_else(|| anyhow::anyhow!("Unexpected observation type"))?;
        anyhow::ensure!(
            data.data_type == signal_type(),
            "Unexpected observation route"
        );
        self.received
            .borrow_mut()
            .push((payload.value, payload.ts_event, payload.ts_init));
        Ok(())
    }
}

#[test]
fn market_input_reaches_strategy_only_through_actor_publication() -> anyhow::Result<()> {
    let instrument = InstrumentAny::CurrencyPair(
        CurrencyPair::builder()
            .instrument_id(InstrumentId::from("AUD/USD.SIM"))
            .raw_symbol(Symbol::from("AUD/USD"))
            .base_currency(Currency::from("AUD"))
            .quote_currency(Currency::from("USD"))
            .price_precision(5)
            .size_precision(0)
            .price_increment(Price::from("0.00001"))
            .size_increment(Quantity::from("1"))
            .ts_event(0_u64.into())
            .ts_init(0_u64.into())
            .build()?,
    );
    let received = Received::default();
    let mut engine = BacktestEngine::new(BacktestEngineConfig::default())?;
    let outcome = (|| -> anyhow::Result<()> {
        engine.add_venue(
            SimulatedVenueConfig::builder()
                .venue(Venue::from("SIM"))
                .oms_type(OmsType::Netting)
                .account_type(AccountType::Margin)
                .book_type(BookType::L1_MBP)
                .starting_balances(vec![Money::from("100000 USD")])
                .build()?,
        )?;
        engine.add_instrument(&instrument)?;
        engine.add_actor(QuotePublisher {
            core: DataActorCore::new(DataActorConfig {
                actor_id: Some(ActorId::from("QUOTE-PUBLISHER-001")),
                ..Default::default()
            }),
            instrument_id: instrument.id(),
            sequence: 0,
        })?;
        engine.add_strategy(ObservationConsumer {
            core: StrategyCore::new_checked(
                StrategyConfig::builder()
                    .strategy_id(StrategyId::from("OBSERVATION-CONSUMER-001"))
                    .order_id_tag("001".to_owned())
                    .build()?,
            )?,
            received: Rc::clone(&received),
        })?;

        let start = 1_735_689_600_000_000_000_u64;
        let expected: Vec<_> = (0..4_u64)
            .map(|i| {
                let event = start + i * 1_000_000_000;
                (
                    (i + 1) as i64,
                    UnixNanos::from(event),
                    UnixNanos::from(event + 50),
                )
            })
            .collect();
        let input = expected
            .iter()
            .map(|(_, event, available)| {
                Data::Quote(QuoteTick::new(
                    instrument.id(),
                    Price::from("0.65000"),
                    Price::from("0.65020"),
                    Quantity::from("100000"),
                    Quantity::from("100000"),
                    *event,
                    *available,
                ))
            })
            .collect();
        engine.add_data(input, None, true, true)?;
        engine.run(None, None, Some("observation-chain".to_owned()), false)?;
        let result = engine.get_result();
        anyhow::ensure!(
            result.iterations == 4,
            "Only four market inputs are allowed"
        );
        anyhow::ensure!(
            *received.borrow() == expected,
            "Derived sequence or time mismatch"
        );
        anyhow::ensure!(result.total_orders == 0, "Delivery requires no orders");
        anyhow::ensure!(result.total_positions == 0, "Delivery creates no exposure");
        Ok(())
    })();
    engine.dispose();
    outcome
}
