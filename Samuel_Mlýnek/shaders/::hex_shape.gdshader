shader_type canvas_item;

// Color of the hex
@uniform color color : source_color = vec4(1.0, 1.0, 1.0, 1.0);

// Border color (black)
@uniform color border_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);

// Thickness of the inner border (try 0.05–0.1)
@uniform float border_thickness = 0.05;

// Function to calculate distance from hex center to edge
float hex_distance(vec2 p) {
    p = abs(p);
    return max(dot(p, normalize(vec2(1.0, sqrt(3.0)))), p.x);
}

void fragment() {
    // Center UV around (0,0) and scale
    vec2 uv = (UV - vec2(0.5)) * 2.0;
    float d = hex_distance(uv);

    // Only draw inside the hex shape
    if (d > 1.0) {
        discard;
    }

    // Determine where the inner border starts
    float t = smoothstep(1.0 - border_thickness, 1.0, d);

    // Mix between border color and main color
    COLOR = mix(border_color, color, t);
}
