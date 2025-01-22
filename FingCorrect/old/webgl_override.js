(function () {
    const webGLProfile = {
        vendor: "NVIDIA Corporation",
        renderer: "GeForce GTX 3060 OpenGL Engine"
    };

    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
    const handler = {
        apply: function (target, thisArg, args) {
            const param = args[0];
            if (param === thisArg.VENDOR) {
                return webGLProfile.vendor;
            }
            if (param === thisArg.RENDERER) {
                return webGLProfile.renderer;
            }
            return Reflect.apply(target, thisArg, args);
        },
        get: function (target, prop) {
            if (prop === "toString") {
                return () => "function getParameter() { [native code] }";
            }
            return Reflect.get(target, prop);
        }
    };

    WebGLRenderingContext.prototype.getParameter = new Proxy(originalGetParameter, handler);
    console.log("WebGL profile secured and overridden:", webGLProfile);
})();
