#include <EGL/egl.h>
#include <GL/gl.h>
#include <string.h>
#include <stdio.h>

// Оригинальная функция (определяется компилятором динамически)
const char* (*real_glGetString)(GLenum name) = NULL;
const char* (*real_eglGetString)(EGLenum name) = NULL;

// Перехват glGetString
const char* glGetString(GLenum name) {
    if (!real_glGetString) {
        real_glGetString = (const char* (*)(GLenum))dlsym(RTLD_NEXT, "glGetString");
    }

    if (name == GL_VENDOR) {
        fprintf(stderr, "Intercepted glGetString: VENDOR\n");
        return "CustomVendor";
    }
    if (name == GL_RENDERER) {
        fprintf(stderr, "Intercepted glGetString: RENDERER\n");
        return "CustomRenderer";
    }

    return real_glGetString(name);
}

// Перехват eglGetString
const char* eglGetString(EGLenum name) {
    if (!real_eglGetString) {
        real_eglGetString = (const char* (*)(EGLenum))dlsym(RTLD_NEXT, "eglGetString");
    }

    if (name == EGL_VENDOR) {
        fprintf(stderr, "Intercepted eglGetString: VENDOR\n");
        return "CustomVendor";
    }
    if (name == EGL_RENDERER) {
        fprintf(stderr, "Intercepted eglGetString: RENDERER\n");
        return "CustomRenderer";
    }

    return real_eglGetString(name);
}
