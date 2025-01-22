// test-frame.js
(function(){
    "use strict";

    // Заглушки для зависимостей
    const mockIntercept = ({ subject }) => {
        console.log("Intercept called with:", subject);
    };
    const mockSettings = {
        get: () => true,
    };
    const mockLogging = {
        message: console.log,
        notice: console.log,
        error: console.error,
    };

    // Вставляем код frame.js с заменой require
    (function(require){
        const { preIntercept: intercept } = require("./intercept");
        const settings = require("./settings");
        const logging = require("./logging");

        let enabled = true;
        logging.message("Starting test frame script");

        function interceptWindow(window) {
            if (!enabled) {
                logging.notice("Intercepting is disabled.");
                return false;
            }

            logging.message("Intercepting window", window);

            intercept(
                { subject: window },
                {
                    check: () => ({ mode: "allow" }),
                    checkStack: () => true,
                    ask: () => "allow",
                    notify: () => {},
                    prefs: (...args) => settings.get(...args),
                }
            );
            return true;
        }

        // Запуск перехвата для текущего окна (тестовое окружение)
        interceptWindow({ location: "https://example.com" });
    })({
        "./intercept": { preIntercept: mockIntercept },
        "./settings": mockSettings,
        "./logging": mockLogging,
    });
})();
