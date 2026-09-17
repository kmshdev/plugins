use std::{env, fs, rc::Rc, str::FromStr};

use anyhow::Context;
use nautilus_backtest::{
    config::{BacktestEngineConfig, SimulatedVenueConfig},
    engine::BacktestEngine,
};
use nautilus_model::{
    data::{Data, QuoteTick},
    enums::{AccountType, BookType, OmsType, OrderSide},
    identifiers::{InstrumentId, StrategyId, Symbol, Venue},
    instruments::{CurrencyPair, Equity, Instrument, InstrumentAny},
    orders::Order,
    types::{Currency, Money, Price, Quantity},
};
use nautilus_skill_quickstart::{EntryParameters, Observations, OneShot, QuoteCounter, signal};
use serde::Deserialize;

const START: u64 = 1_735_689_600_000_000_000;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct RunConfig {
    run_label: String,
    venue: String,
    instrument: InstrumentConfig,
    entry: EntryConfig,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
enum InstrumentConfig {
    Fx {
        instrument_id: String,
        raw_symbol: String,
        base_currency: String,
        quote_currency: String,
        price_precision: u8,
        size_precision: u8,
        price_increment: String,
        size_increment: String,
        bid: String,
        ask: String,
        quote_quantity: String,
    },
    Equity {
        instrument_id: String,
        raw_symbol: String,
        currency: String,
        price_precision: u8,
        price_increment: String,
        lot_size: String,
        bid: String,
        ask: String,
        quote_quantity: String,
    },
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct EntryConfig {
    strategy_id: String,
    side: EntrySide,
    quantity: String,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
enum EntrySide {
    Buy,
    Sell,
}

impl EntrySide {
    const fn into_order_side(self) -> OrderSide {
        match self {
            Self::Buy => OrderSide::Buy,
            Self::Sell => OrderSide::Sell,
        }
    }
}

#[derive(Debug)]
struct ConfiguredInstrument {
    instrument: InstrumentAny,
    bid: Price,
    ask: Price,
    quote_quantity: Quantity,
    quantity_increment: Quantity,
    quantity_precision: u8,
}

impl ConfiguredInstrument {
    fn validate_entry_quantity(&self, value: &str) -> anyhow::Result<Quantity> {
        parse_quantity(
            value,
            self.quantity_precision,
            self.quantity_increment,
            "entry.quantity",
        )
    }
}

impl InstrumentConfig {
    fn build(&self, venue: Venue) -> anyhow::Result<ConfiguredInstrument> {
        match self {
            Self::Fx {
                instrument_id,
                raw_symbol,
                base_currency,
                quote_currency,
                price_precision,
                size_precision,
                price_increment,
                size_increment,
                bid,
                ask,
                quote_quantity,
            } => {
                let instrument_id = parse_instrument_id(instrument_id, venue)?;
                let price_increment =
                    parse_increment(price_increment, *price_precision, "price_increment")?;
                let size_increment =
                    parse_quantity_increment(size_increment, *size_precision, "size_increment")?;
                let bid = parse_price(bid, *price_precision, price_increment, "bid")?;
                let ask = parse_price(ask, *price_precision, price_increment, "ask")?;
                anyhow::ensure!(
                    ask.raw() >= bid.raw(),
                    "ask must be greater than or equal to bid"
                );
                let quote_quantity = parse_quantity(
                    quote_quantity,
                    *size_precision,
                    size_increment,
                    "quote_quantity",
                )?;
                let instrument = InstrumentAny::CurrencyPair(
                    CurrencyPair::builder()
                        .instrument_id(instrument_id)
                        .raw_symbol(parse_symbol(raw_symbol, "raw_symbol")?)
                        .base_currency(parse_currency(base_currency, "base_currency")?)
                        .quote_currency(parse_currency(quote_currency, "quote_currency")?)
                        .price_precision(*price_precision)
                        .size_precision(*size_precision)
                        .price_increment(price_increment)
                        .size_increment(size_increment)
                        .ts_event(0_u64.into())
                        .ts_init(0_u64.into())
                        .build()?,
                );
                Ok(ConfiguredInstrument {
                    instrument,
                    bid,
                    ask,
                    quote_quantity,
                    quantity_increment: size_increment,
                    quantity_precision: *size_precision,
                })
            }
            Self::Equity {
                instrument_id,
                raw_symbol,
                currency,
                price_precision,
                price_increment,
                lot_size,
                bid,
                ask,
                quote_quantity,
            } => {
                let instrument_id = parse_instrument_id(instrument_id, venue)?;
                let price_increment =
                    parse_increment(price_increment, *price_precision, "price_increment")?;
                let lot_size = parse_nonzero_quantity(lot_size, "lot_size")?;
                let bid = parse_price(bid, *price_precision, price_increment, "bid")?;
                let ask = parse_price(ask, *price_precision, price_increment, "ask")?;
                anyhow::ensure!(
                    ask.raw() >= bid.raw(),
                    "ask must be greater than or equal to bid"
                );
                let quote_quantity = parse_quantity(
                    quote_quantity,
                    lot_size.precision,
                    lot_size,
                    "quote_quantity",
                )?;
                let instrument = InstrumentAny::Equity(
                    Equity::builder()
                        .instrument_id(instrument_id)
                        .raw_symbol(parse_symbol(raw_symbol, "raw_symbol")?)
                        .currency(parse_currency(currency, "currency")?)
                        .price_precision(*price_precision)
                        .price_increment(price_increment)
                        .lot_size(lot_size)
                        .ts_event(0_u64.into())
                        .ts_init(0_u64.into())
                        .build()?,
                );
                Ok(ConfiguredInstrument {
                    instrument,
                    bid,
                    ask,
                    quote_quantity,
                    quantity_increment: lot_size,
                    quantity_precision: lot_size.precision,
                })
            }
        }
    }
}

impl RunConfig {
    fn load() -> anyhow::Result<Self> {
        let mut arguments = env::args_os();
        let _program = arguments.next();
        let Some(path) = arguments.next() else {
            anyhow::ensure!(
                arguments.next().is_none(),
                "Expected at most one JSON configuration path"
            );
            return Ok(Self::default());
        };
        anyhow::ensure!(
            arguments.next().is_none(),
            "Expected at most one JSON configuration path"
        );
        let contents = fs::read_to_string(&path)
            .with_context(|| format!("Failed to read configuration {}", path.to_string_lossy()))?;
        serde_json::from_str(&contents)
            .with_context(|| format!("Failed to parse configuration {}", path.to_string_lossy()))
    }
}

impl Default for RunConfig {
    fn default() -> Self {
        Self {
            run_label: "skill-quickstart".to_owned(),
            venue: "SIM".to_owned(),
            instrument: InstrumentConfig::Fx {
                instrument_id: "AUD/USD.SIM".to_owned(),
                raw_symbol: "AUD/USD".to_owned(),
                base_currency: "AUD".to_owned(),
                quote_currency: "USD".to_owned(),
                price_precision: 5,
                size_precision: 0,
                price_increment: "0.00001".to_owned(),
                size_increment: "1".to_owned(),
                bid: "0.65000".to_owned(),
                ask: "0.65020".to_owned(),
                quote_quantity: "100000".to_owned(),
            },
            entry: EntryConfig {
                strategy_id: "ONE-SHOT-001".to_owned(),
                side: EntrySide::Buy,
                quantity: "1000".to_owned(),
            },
        }
    }
}

fn main() -> anyhow::Result<()> {
    let config = RunConfig::load()?;
    let venue = Venue::new_checked(&config.venue).context("Invalid venue")?;
    let configured_instrument = config.instrument.build(venue)?;
    let instrument_id = configured_instrument.instrument.id();
    let strategy_id =
        StrategyId::new_checked(&config.entry.strategy_id).context("Invalid entry.strategy_id")?;
    let entry = EntryParameters {
        instrument_id,
        side: config.entry.side.into_order_side(),
        quantity: configured_instrument.validate_entry_quantity(&config.entry.quantity)?,
        strategy_id,
    };

    let observations = Rc::new(Observations::default());
    let mut engine = BacktestEngine::new(BacktestEngineConfig::default())?;
    engine.add_venue(
        SimulatedVenueConfig::builder()
            .venue(venue)
            .oms_type(OmsType::Netting)
            .account_type(AccountType::Margin)
            .book_type(BookType::L1_MBP)
            .starting_balances(vec![Money::from("100000 USD")])
            .build()?,
    )?;
    engine.add_instrument(&configured_instrument.instrument)?;
    engine.add_actor(QuoteCounter::new(instrument_id, Rc::clone(&observations)))?;
    engine.add_strategy(OneShot::new(entry)?)?;

    let quotes = (0..4_u64)
        .map(|index| {
            let timestamp = START + index * 1_000_000_000;
            Data::Quote(QuoteTick::new(
                instrument_id,
                configured_instrument.bid,
                configured_instrument.ask,
                configured_instrument.quote_quantity,
                configured_instrument.quote_quantity,
                timestamp.into(),
                timestamp.into(),
            ))
        })
        .collect();
    engine.add_data(quotes, None, true, true)?;
    engine.add_data(
        vec![Data::Custom(signal(
            7,
            START.into(),
            (START + 500_000_000).into(),
        ))],
        None,
        true,
        true,
    )?;

    let outcome = (|| -> anyhow::Result<()> {
        engine.run(None, None, Some(config.run_label), false)?;
        let result = engine.get_result();
        anyhow::ensure!(result.iterations == 5, "Expected five replay inputs");
        anyhow::ensure!(observations.quotes.get() == 4, "Quote dispatch mismatch");
        anyhow::ensure!(observations.signals.get() == 1, "Custom dispatch mismatch");
        anyhow::ensure!(result.total_orders == 1, "Expected one order, not a loop");
        anyhow::ensure!(result.total_positions == 1, "Expected simulated exposure");

        let cache = engine.kernel().cache();
        let cache = cache.borrow();
        let orders = cache.orders(None, Some(&instrument_id), Some(&strategy_id), None, None);
        anyhow::ensure!(orders.len() == 1, "Expected exactly one cached order");
        let positions = cache.positions(None, Some(&instrument_id), Some(&strategy_id), None, None);
        anyhow::ensure!(positions.len() == 1, "Expected exactly one cached position");
        let order = &orders[0];
        let position = &positions[0];
        anyhow::ensure!(
            order.filled_qty() == order.quantity(),
            "Order was not fully filled"
        );
        anyhow::ensure!(
            position.quantity == order.filled_qty(),
            "Cached position quantity did not match filled order quantity"
        );
        println!(
            "inputs={} quotes={} signals={} orders={} positions={}",
            result.iterations,
            observations.quotes.get(),
            observations.signals.get(),
            result.total_orders,
            result.total_positions,
        );
        println!(
            "filled_quantity={} position_quantity={} position_side={:?}",
            order.filled_qty(),
            position.quantity,
            position.side,
        );
        Ok(())
    })();
    engine.dispose();
    outcome
}

fn parse_instrument_id(value: &str, venue: Venue) -> anyhow::Result<InstrumentId> {
    let instrument_id = InstrumentId::from_str(value).context("Invalid instrument_id")?;
    anyhow::ensure!(
        instrument_id.venue == venue,
        "instrument_id venue {} must match venue {}",
        instrument_id.venue,
        venue
    );
    Ok(instrument_id)
}

fn parse_symbol(value: &str, field: &str) -> anyhow::Result<Symbol> {
    Symbol::new_checked(value).with_context(|| format!("Invalid {field}"))
}

fn parse_currency(value: &str, field: &str) -> anyhow::Result<Currency> {
    Currency::from_str(value).with_context(|| format!("Invalid {field}"))
}

fn parse_increment(value: &str, precision: u8, field: &str) -> anyhow::Result<Price> {
    let increment = parse_positive_price(value, field)?;
    anyhow::ensure!(
        increment.precision == precision,
        "{field} precision {} must equal price_precision {precision}",
        increment.precision
    );
    Ok(increment)
}

fn parse_price(value: &str, precision: u8, increment: Price, field: &str) -> anyhow::Result<Price> {
    let price = parse_positive_price(value, field)?;
    anyhow::ensure!(
        price.precision <= precision,
        "{field} precision {} exceeds price_precision {precision}",
        price.precision
    );
    anyhow::ensure!(
        price.raw() % increment.raw() == 0,
        "{field} must be on the price grid"
    );
    Ok(price)
}

fn parse_positive_price(value: &str, field: &str) -> anyhow::Result<Price> {
    let price =
        Price::from_str(value).map_err(|error| anyhow::anyhow!("Invalid {field}: {error}"))?;
    anyhow::ensure!(price.raw() > 0, "{field} must be positive");
    Ok(price)
}

fn parse_quantity_increment(value: &str, precision: u8, field: &str) -> anyhow::Result<Quantity> {
    let increment = parse_nonzero_quantity(value, field)?;
    anyhow::ensure!(
        increment.precision == precision,
        "{field} precision {} must equal size_precision {precision}",
        increment.precision
    );
    Ok(increment)
}

fn parse_quantity(
    value: &str,
    precision: u8,
    increment: Quantity,
    field: &str,
) -> anyhow::Result<Quantity> {
    let quantity = parse_nonzero_quantity(value, field)?;
    anyhow::ensure!(
        quantity.precision <= precision,
        "{field} precision {} exceeds supported precision {precision}",
        quantity.precision
    );
    anyhow::ensure!(
        quantity.raw() % increment.raw() == 0,
        "{field} must be on the quantity grid"
    );
    Ok(quantity)
}

fn parse_nonzero_quantity(value: &str, field: &str) -> anyhow::Result<Quantity> {
    let quantity =
        Quantity::from_str(value).map_err(|error| anyhow::anyhow!("Invalid {field}: {error}"))?;
    anyhow::ensure!(!quantity.is_zero(), "{field} must be positive");
    Ok(quantity)
}
