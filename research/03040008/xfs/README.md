# XFS samples, client 03040008

This directory holds samples of client 03040008 files in the XFS container as readable dumps, for anyone comparing a format's fields by hand. Each sample has a `.txt` view of its header and structures (`XFS (v1)`, `version`, `structCount`) and, for most, an `.xml` view of its values. The conversion tool is not recorded, so treat them as fixed samples; they came in with the commits around `a6ce2dcc449` and `c625090c6f5`. The documentation map is [`docs/index.md`](../../../docs/index.md).

The name of a sample is the client file's name plus the view: `LdParam.ldp.txt`, `LdParam.ldp.xml`.
