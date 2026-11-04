# Apply a client patch

This page is for anyone who needs one of the recorded PC 03040008 executables and holds its parent. You apply one `.r2` layer to a copy and check the hash it must produce. You need `radare2` and `rahash2` on `PATH` and the parent executable; [Client patches](../reference/client-patches.md) lists every layer with its starting and target hash.

## Steps

The commands were run with radare2 6.1.0 on a scratch file, never on an executable: [Status](../reference/status.md#client-patches).

1. Find the layer's row in [Client patches](../reference/client-patches.md#patched-executables), and work on a copy, since the write is in place:

   ```bash
   cp -p <parent>.exe <target>.exe
   ```

2. Check that the copy is the row's Starting Hash:

   ```bash
   rahash2 -a sha256 <target>.exe
   ```

   Stop on a difference. A `.r2` is a sequence of "write these bytes at this offset" commands with no check of its own, so on the wrong base it **silently corrupts the binary**.

3. Apply the layer. Every tracked `.r2` file except `rootofallthings_chat_edit.r2` and `bunie_5_in_1.r2` is UTF-16 ([count](../reference/status.md#client-patches)), and radare2 6.1.0 does not run UTF-16: it prints `Invalid command`, writes nothing and goes on. Convert those files first:

   ```bash
   iconv -f UTF-16 -t UTF-8 patches/<layer>.r2 > <layer>.utf8.r2
   radare2 -qnw -i <layer>.utf8.r2 <target>.exe
   ```

   | Flag | Purpose |
   | --- | --- |
   | `-q` | Quit after executing the script |
   | `-n` | Do not load or parse binary headers |
   | `-w` | Open the file in read-write mode |
   | `-i` | The `.r2` script to run |

4. Check the result against the row's Target Hash:

   ```bash
   rahash2 -a sha256 <target>.exe
   ```

   An equal hash is success; there is no other sign. On a difference, delete the copy and start from step 1. The hash of step 2 again means nothing was written: look for `Invalid command` in step 3.

## Layers in order

Layers stack, so **order matters**: apply them in the order of the lineage, each on the exact Target Hash of the layer before it. Rows with `(none)` in the Patch column have no `.r2` and exist only as executables. Several layers start from `f1c9`: they are alternatives, and the second of them does not apply on top of the first.

The `DDO_DUMP_FIX` row replays from the Mutex build `9c95` but writes its bytes back, so its result holds no Mutex patch ([lineage](../reference/client-patches.md#lineage)).
