# Client patches

The binary diffs of the Windows `DDO.exe` builds: one `.r2` radare2 script and one `.json` per layer, hand-written or written by `radiff2`. Each layer starts from a stated SHA-256 and must produce another.

- [Apply a client patch](../docs/how-to/apply-a-client-patch.md)
- [Add a client patch layer](../docs/how-to/add-a-client-patch-layer.md)
- [Client patches](../docs/reference/client-patches.md): the hash chain, the lineage, file offsets and the encoding of these files
- [Client lineage and protections](../docs/explanation/client-lineage-and-protections.md): what the layers do and why
