# LLM prompts for ddon-extractor

This directory holds hand-written LLM prompts that convert C++ class definitions into ddon-extractor Java, for anyone adding a resource type there. No script reads them. The documentation map is [`docs/index.md`](../../docs/index.md).

| File | Converts C++ structures to |
| --- | --- |
| `gpt-java-class-prompt.txt` | Java classes |
| `gpt-java-record-prompt.txt` | Java records |
| `gpt-map-deserializer-methods.txt` | deserializer methods |
