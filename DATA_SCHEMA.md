# Database schema

`events`: raw market snapshots and derived feature events.
`trades`: reconstructable execution summary including fees, slippage, holding time and decision metadata.
`predictions`: model predictions and expected returns.
`errors`: component errors and timestamps.

Raw market snapshots are JSON so the original exchange payload can be replayed after parser improvements.
