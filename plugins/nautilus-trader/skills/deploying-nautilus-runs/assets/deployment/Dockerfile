FROM rust:1.98.1-bookworm AS build
WORKDIR /build
COPY . .
RUN cargo build --release --locked --package @@PACKAGE@@ --bin @@BINARY@@

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libssl3 && rm -rf /var/lib/apt/lists/* && mkdir -p /data && chown 10001:10001 /data
COPY --from=build /build/target/release/@@BINARY@@ /usr/local/bin/runner
USER 10001:10001
WORKDIR /data
ENTRYPOINT ["/usr/local/bin/runner"]
