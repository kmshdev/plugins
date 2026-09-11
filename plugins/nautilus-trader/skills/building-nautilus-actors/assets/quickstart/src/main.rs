use std::rc::Rc;

use nautilus_backtest::{
    config::{BacktestEngineConfig, SimulatedVenueConfig},
    engine::BacktestEngine,
};
use nautilus_model::{
    data::{Data, QuoteTick},
    enums::{AccountType, BookType, OmsType},
    identifiers::{InstrumentId, Symbol, Venue},
    instruments::{CurrencyPair, Instrument, InstrumentAny},
    types::{Currency, Money, Price, Quantity},
};
use nautilus_skill_quickstart::{Observations, QuoteCounter, signal};

fn main() -> anyhow::Result<()> {
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
    let instrument_id = instrument.id();
    let observations = Rc::new(Observations::default());
    let mut engine = BacktestEngine::new(BacktestEngineConfig::default())?;
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
    engine.add_actor(QuoteCounter::new(instrument_id, Rc::clone(&observations)))?;

    let start = 1_735_689_600_000_000_000_u64;
    let quotes = (0..4_u64)
        .map(|i| {
            let ts = start + i * 1_000_000_000;
            Data::Quote(QuoteTick::new(
                instrument_id,
                Price::from("0.65000"),
                Price::from("0.65020"),
                Quantity::from("100000"),
                Quantity::from("100000"),
                ts.into(),
                ts.into(),
            ))
        })
        .collect();
    engine.add_data(quotes, None, true, true)?;
    engine.add_data(
        vec![Data::Custom(signal(
            7,
            start.into(),
            (start + 500_000_000).into(),
        ))],
        None,
        true,
        true,
    )?;

    let outcome = (|| -> anyhow::Result<()> {
        engine.run(None, None, Some("actor-quickstart".to_owned()), false)?;
        let result = engine.get_result();
        anyhow::ensure!(result.iterations == 5, "Expected five replay inputs");
        anyhow::ensure!(observations.quotes.get() == 4, "Quote dispatch mismatch");
        anyhow::ensure!(observations.signals.get() == 1, "Custom dispatch mismatch");
        anyhow::ensure!(result.total_orders == 0, "Actors must not submit orders");
        anyhow::ensure!(result.total_positions == 0, "Unexpected simulated exposure");
        println!(
            "inputs={} quotes={} signals={} orders={} positions={}",
            result.iterations,
            observations.quotes.get(),
            observations.signals.get(),
            result.total_orders,
            result.total_positions,
        );
        Ok(())
    })();
    engine.dispose();
    outcome
}
