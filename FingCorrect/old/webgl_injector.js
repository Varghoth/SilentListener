// webgl_injector.js
(function () {
    const scriptContent = `
        (function () {
            const webGLProfile = {
                vendor: "NVIDIA Corporation",
                renderer: "GeForce GTX 3060 OpenGL Engine"
            };

            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function (param) {
                if (param === this.VENDOR) {
                    return webGLProfile.vendor;
                }
                if (param === this.RENDERER) {
                    return webGLProfile.renderer;
                }
                return originalGetParameter.call(this, param);
            };

            console.log("WebGL profile overridden:", webGLProfile);
        })();
    `;

    const scriptElement = document.createElement("script");
    scriptElement.textContent = scriptContent;
    (document.head || document.documentElement).appendChild(scriptElement);
    scriptElement.remove();
})();
