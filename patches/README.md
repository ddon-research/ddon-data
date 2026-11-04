# Client patches

The binary diffs of the Windows `DDO.exe` builds: one `.r2` radare2 script and one `.json` per layer, hand-authored or written by `radiff2`. The original packed client was dumped unpacked with Ghidra, Scylla and others. Layers of 2020–2022 removed anti-tampering, anti-cheating and anti-debugging protections to enable research; layers from 2025 on improve quality of life. Each layer starts from a stated SHA-256 and must produce another, so the chain from the vanilla client through every layer stays verifiable.

- [Apply a client patch](../docs/how-to/apply-a-client-patch.md)
- [Add a client patch layer](../docs/how-to/add-a-client-patch-layer.md)
- [Client patches](../docs/reference/client-patches.md): the hash chain, the lineage, file offsets and the encoding of these files
- [Client lineage and protections](../docs/explanation/client-lineage-and-protections.md): what the layers do and why

`2026_10_17_*` is another layer, not tracked at 2026-11-04.
