shader_type spatial;

uniform sampler2D albedo_texture : source_color, repeat_enable;
uniform sampler2D roughness_texture : repeat_enable;
uniform sampler2D normal_texture : hint_normal, repeat_enable;

group_uniforms surface;
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float uv_scale : hint_range(0.25, 8.0) = 1.0;
group_uniforms;

group_uniforms detail;
uniform float roughness_scale : hint_range(0.0, 1.0) = 1.0;
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
group_uniforms;

void fragment() {
	vec2 uv = UV * uv_scale;
	ALBEDO = texture(albedo_texture, uv).rgb * tint.rgb;
	ROUGHNESS = texture(roughness_texture, uv).r * roughness_scale;
	NORMAL_MAP = texture(normal_texture, uv).rgb;
	NORMAL_MAP_DEPTH = normal_strength;
}
