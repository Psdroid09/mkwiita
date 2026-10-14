# MKWiita / PSdroid09: first performance pass

This fork tracks the original project at https://github.com/boomannotjeff/mkwiita.
Original credits, copyrights, and license notices remain unchanged.

## Changes in this experimental branch

1. **Framebuffer binding cache:** avoid calling `glBindFramebuffer` when the requested framebuffer is already bound. Track framebuffer creation, readback, and deletion so the cache is invalidated after GL state can change externally.
2. **Optional GPU profiling:** costly per-draw timing and per-300-frame `glFinish()` sampling now run only if the user explicitly enables GPU statistics. This avoids forcing a GPU synchronization periodically during normal play. Shader cache and gameplay logic are unchanged.
3. **No rendering-resolution or framerate changes:** native rendering size, VSync and gameplay pacing are deliberately preserved. The changes aim to reduce driver overhead/hitches, **not** claim 60 FPS.

## Enable profiling for a comparison

- Create an empty file named `ux0:data/mkw/gpu-stats.txt` using VitaShell, **before launching MKWiita**.
- Play a reproducible race for at least 60 seconds after shader cache warm-up. Collect `ux0:data/mkw/vita.log`.
- Compare the same course, racers and options between the original VPK and a build from this branch, ideally with the same PSVShell clocks. Compare FPS and hitches, not just peak FPS.
- Delete `gpu-stats.txt` and restart the game for the optimized normal-play mode.

Optional existing debug switches remain available (`gpu-trace.txt`, `gpu-sync.txt`); **do not** turn on `gpu-sync.txt` during normal performance comparisons because it intentionally waits for the GPU every frame.

## Testing status / caution

- Source reviewed and patch committed; **not compiled with VitaSDK and not verified on actual PS Vita hardware here**.
- No VPK is included with these changes. Compile with VitaSDK following the upstream `BUILDING.md` instructions.
- These changes may have no measurable FPS effect if the GPU, game logic or audio is the bottleneck. A 60 FPS promise would be misleading.
- If you see missing or stale graphics after testing, revert to the original VPK and report your `vita.log`.

## Próximos pasos

Medir escenarios donde aparezcan tirones, verificar los tiempos con `gpu-stats.txt`, revisar el número de cambios de render target por fotograma y continuar con optimizaciones basadas en resultados reales. Evitar cambiar física, sonido o sincronización sin pruebas en la consola.
