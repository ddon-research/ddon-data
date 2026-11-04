# DTI class dumps, client 03040008

This directory holds the runtime type (DTI) table of the PC client 03040008, dumped from memory, for anyone looking up a class's size, id or parent. The files are a fixed dump: no script here regenerates them, and they came in with commit `09cbd3aad0f`. The documentation map is [`docs/index.md`](../../../docs/index.md).

| File | Holds |
| --- | --- |
| `dti.csv` | one row per class, with the header `#index,class_name,parent_name,size_param,size_decoded,id_hex,attr,alloc_idx,this_addr,parent_addr,vptr` |
| `dti-class-name.txt` | the class names alone, in the same order |
