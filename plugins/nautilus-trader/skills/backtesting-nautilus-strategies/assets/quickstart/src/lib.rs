use nautilus_common::{actor::DataActor, log_warn};
use nautilus_model::{
    data::QuoteTick,
    enums::OrderSide,
    events::OrderRejected,
    identifiers::{ClientOrderId, InstrumentId, StrategyId},
    instruments::Instrument,
    orders::Order,
    types::Quantity,
};
use nautilus_trading::{
    nautilus_strategy,
    strategy::{Strategy, StrategyConfig, StrategyCore},
};

mod observer;
pub use observer::{Observations, QuoteCounter, SignalV1, signal, signal_type};

#[derive(Debug)]
pub struct OneShot {
    core: StrategyCore,
    instrument_id: InstrumentId,
    side: OrderSide,
    quantity: Quantity,
    attempted: bool,
    entry_id: Option<ClientOrderId>,
}

#[derive(Debug)]
pub struct EntryParameters {
    pub instrument_id: InstrumentId,
    pub side: OrderSide,
    pub quantity: Quantity,
    pub strategy_id: StrategyId,
}

impl OneShot {
    pub fn new(parameters: EntryParameters) -> anyhow::Result<Self> {
        let config = StrategyConfig::builder()
            .strategy_id(parameters.strategy_id)
            .order_id_tag(parameters.strategy_id.get_tag().to_owned())
            .build()?;
        Ok(Self {
            core: StrategyCore::new_checked(config)?,
            instrument_id: parameters.instrument_id,
            side: parameters.side,
            quantity: parameters.quantity,
            attempted: false,
            entry_id: None,
        })
    }
}

nautilus_strategy!(OneShot, {
    fn on_order_rejected(&mut self, event: OrderRejected) {
        log_warn!("One-shot rejection: {}", event.reason);
    }
});

impl DataActor for OneShot {
    fn on_start(&mut self) -> anyhow::Result<()> {
        self.cache().try_instrument(&self.instrument_id)?;
        self.subscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_stop(&mut self) -> anyhow::Result<()> {
        self.unsubscribe_quotes(self.instrument_id, None, None);
        Ok(())
    }

    fn on_reset(&mut self) -> anyhow::Result<()> {
        self.attempted = false;
        self.entry_id = None;
        Ok(())
    }

    fn on_quote(&mut self, quote: &QuoteTick) -> anyhow::Result<()> {
        if quote.instrument_id != self.instrument_id || self.attempted {
            return Ok(());
        }
        let instrument = self.cache().try_instrument(&self.instrument_id)?;
        let quantity = instrument.try_normalize_qty(self.quantity)?;
        anyhow::ensure!(
            quantity == self.quantity,
            "Configured quantity {} is off the instrument grid",
            self.quantity
        );
        let order = self.order().market(
            self.instrument_id,
            self.side,
            quantity,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        );
        // Initialization can publish inline; preserve possible-send state on errors.
        self.entry_id = Some(order.client_order_id());
        self.attempted = true;
        self.submit_order(order, None, None, None)?;
        Ok(())
    }
}
