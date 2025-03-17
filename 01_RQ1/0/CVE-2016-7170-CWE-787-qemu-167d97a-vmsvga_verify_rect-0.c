static inline bool vmsvga_verify_rect(DisplaySurface *surface,
                                      const char *name,
                                      int x, int y, int w, int h)
{
    if (x < 0) {
        fprintf(stderr, "%s: x was < 0 (%d)\n", name, x);
        return false;
    }
    if (x > SVGA_MAX_WIDTH) {
        fprintf(stderr, "%s: x was > %d (%d)\n", name, SVGA_MAX_WIDTH, x);
        return false;
    }
    if (w < 0) {
        fprintf(stderr, "%s: w was < 0 (%d)\n", name, w);
        return false;
    }
    if (w > SVGA_MAX_WIDTH) {
        fprintf(stderr, "%s: w was > %d (%d)\n", name, SVGA_MAX_WIDTH, w);
        return false;
    }
    if (x + w > surface_width(surface)) {
        fprintf(stderr, "%s: width was > %d (x: %d, w: %d)\n",
                name, surface_width(surface), x, w);
        return false;
    }

    if (y < 0) {
        fprintf(stderr, "%s: y was < 0 (%d)\n", name, y);
        return false;
    }
    if (y > SVGA_MAX_HEIGHT) {
        fprintf(stderr, "%s: y was > %d (%d)\n", name, SVGA_MAX_HEIGHT, y);
        return false;
    }
    if (h < 0) {
        fprintf(stderr, "%s: h was < 0 (%d)\n", name, h);
        return false;
    }
    if (h > SVGA_MAX_HEIGHT) {
        fprintf(stderr, "%s: h was > %d (%d)\n", name, SVGA_MAX_HEIGHT, h);
        return false;
    }
    if (y + h > surface_height(surface)) {
        fprintf(stderr, "%s: update height > %d (y: %d, h: %d)\n",
                name, surface_height(surface), y, h);
        return false;
    }

    return true;
}
