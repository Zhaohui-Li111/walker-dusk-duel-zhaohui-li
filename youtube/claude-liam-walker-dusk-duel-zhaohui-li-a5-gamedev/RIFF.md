# RIFF — observations behind the commentary

| Artifact + range | Visible observation | Interpretation (source) | Narration | Next experiment |
|---|---|---|---|---|
| capture/flash.avi 0.3-11.0 s (B02) | Akaken's punch lands; Aotake turns solid red, the whole sprite, then fades to its own colours. At about 4.2 s Aotake kicks and only Akaken goes red. | The driver gives each fighter its own material (hurt_flash.gd:19-21); the fade is stun / 18. | "This time only Akaken flashes." | Capture both fighters hit on the same tick. |
| fig_controlled (B05) | Akaken's gi goes from orange to red; at 0.5 the gi is still recognisably orange-red, the fist turns pink. | The red flash changes hue more than brightness on the gi (brief Revision 5: contrast 3.93 → 3.73). | "Within one step of Jow-hway's arithmetic." | Try a white flash colour and compare readability. |
| fig_clamp (B08) | At 2.0 with grey, Akaken turns blue-white, not grey. | `mix` with t = 2 extrapolates past grey: R falls, G and B rise. | "The mix, extrapolated." | Clamp in the shader with `clamp()` and compare. |
| fig_materials (B12) | The floor's granite looks like horizontal boards; the plinth behind the taiko is dark. | BoxMesh UV stretch (MATERIALS.md findings 1-3); the plinth is tinted #6E6680 and partly in shadow. | "It looks like wooden planks." (Zhaohui's words) | A `vec2` UV scale per axis. |
| fig_sweep (B13) | uv_scale 0.25 blurs the floor into a smear; tint black leaves only a faint grey from ambient light. | One copy of the texture stretched over the floor; ambient and reflected light still add a little. | "Tint at black isn't good-looking." (Zhaohui) | Sweep with the ambient light off. |
| fig_hint (B15) | Quad A and quad B look identical, three flat greys each. | Compatibility decodes every ALBEDO (scene.glsl:2398) and encodes on output (:2798). | "Both quads show the stored values." | The same scene in Forward+. |

All observations are Claude's, from the frames and images listed, except where Zhaohui's own words
are quoted (TEST-REPORT A5 human checks).
