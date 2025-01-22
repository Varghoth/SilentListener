(() => {
    console.log("Content script loaded: overriding WebGL and Canvas.");

    // Подмена WebGL Vendor и Renderer
    const overrideWebGL = () => {
        try {
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function (param) {
                // Перехватим VENDOR и RENDERER
                if (param === this.VENDOR) {
                    console.log("Intercepted WebGL Vendor request.");
                    return "Google Inc.";
                }
                if (param === this.RENDERER) {
                    console.log("Intercepted WebGL Renderer request.");
                    return "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)";
                }
                return getParameter.call(this, param);
            };
        } catch (error) {
            console.error("Error overriding WebGL parameters:", error);
        }
    };

    // Подмена Canvas fingerprint
    const overrideCanvas = () => {
        try {
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function (type, encoderOptions) {
                console.log("Canvas data intercepted.");
                // Возвращаем "шумный" фингерпринт
                return "data:image/png;base64,NoisyCanvasFingerprint1";
            };

            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function (type, options) {
                const context = getContext.call(this, type, options);
                if (type === "2d" || type === "webgl" || type === "webgl2") {
                    console.log(`Canvas context '${type}' intercepted.`);
                }
                return context;
            };
        } catch (error) {
            console.error("Error overriding Canvas fingerprinting:", error);
        }
    };

    // Инициализация подмен
    overrideWebGL();
    overrideCanvas();
})();
