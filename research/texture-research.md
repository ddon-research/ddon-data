

```sh
$ grep -h -o -R "\"FORMAT_.*\"" . | sort | uniq

"FORMAT_B4G4R4A4_UNORM"
"FORMAT_B8G8R8A8_UNORM"
"FORMAT_B8G8R8A8_UNORM_SRGB"
"FORMAT_BC1_UNORM"
"FORMAT_BC1_UNORM_SRGB"
"FORMAT_BC2_UNORM_SRGB"
"FORMAT_BC3_UNORM_SRGB"
"FORMAT_BCX_GRAYSCALE"
"FORMAT_BCX_NH"
"FORMAT_BCX_NM2"
"FORMAT_BCX_YCCA_SRGB"
"FORMAT_R32_FLOAT"
```

```sh
$ grep -h -o -R "\"TEXTURE_TYPE_.*\"" . | sort | uniq

"TEXTURE_TYPE_2D"
"TEXTURE_TYPE_CUBE"
```
