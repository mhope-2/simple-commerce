### Useful Timescale DB Shell Commands

1. Enter TimescaleDB shell:
```bash
psql -U <db user>
```
E.g.
```bash
psql -U <postgres>
```

2. Connect to your desired database:
```bash
\c <db name>
```
E.g.
```bash
\c orders
```

3. List tables:
```bash
\dt
```

### Useful RabbitMQ Shell Commands

1. List Exchanges:
```bash
rabbitmqctl list_exchanges
```