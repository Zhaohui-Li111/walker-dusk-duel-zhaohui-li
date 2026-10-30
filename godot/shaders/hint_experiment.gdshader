shader_type spatial;
render_mode unshaded;

uniform sampler2D grey_as_color : source_color, filter_nearest;
uniform sampler2D grey_as_data : filter_nearest;

uniform bool read_as_color = true;

void fragment() {
	if (read_as_color) {
		ALBEDO = texture(grey_as_color, UV).rgb;
	} else {
		ALBEDO = texture(grey_as_data, UV).rgb;
	}
}
