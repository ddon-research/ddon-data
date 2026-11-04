# plbatch

A batch driver for ImHex patterns, hand-written C++ on PatternLanguage: one process runs one pattern over many files and writes one JSON file per input. `packets/imhex-export.sh` uses it when it is built, and `build.sh` writes it to `build/bin/plbatch.exe` (`build/` is gitignored).

- [Build plbatch](../../docs/how-to/build-plbatch.md)
- [plbatch CLI](../../docs/reference/plbatch-cli.md)
- [plbatch design](../../docs/explanation/plbatch-design.md)
