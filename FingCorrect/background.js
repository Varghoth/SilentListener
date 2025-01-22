// Конфигурация для генерации профиля (встроена в код)
const generationConfig = {
    userAgents: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/110.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    ],
    screenResolutions: [
        { width: 2560, height: 1440 },
        { width: 1920, height: 1080 },
        { width: 1680, height: 1050 }
    ],
    deviceMemories: [8, 16, 32],
    hardwareConcurrencies: [4, 6, 8],
    languages: ["en-US", "en-GB", "en-AU"],
    webGL: {
        "Google Inc.": [
            "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (Intel(R) Iris Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (NVIDIA GeForce GTX 1050 Direct3D11 vs_5_0 ps_5_0)"
        ],
        "NVIDIA Corporation": [
            "GeForce RTX 2060 OpenGL Engine",
            "GeForce GTX 1060 OpenGL Engine",
            "GeForce GTX 3060 OpenGL Engine",
            "GeForce GTX 4060 OpenGL Engine"
        ],
        "AMD Inc.": [
            "AMD Radeon RX 5700 OpenGL Engine",
            "AMD Radeon RX 5500 XT OpenGL Engine",
            "AMD Radeon Vega 8 Graphics OpenGL Engine"
        ],
        "Intel Inc.": [
            "Intel(R) HD Graphics 620 OpenGL Engine",
            "Intel(R) UHD Graphics 620 OpenGL Engine",
            "Intel(R) Iris Xe Graphics OpenGL Engine"
        ]
    },
    platforms: ["Win32", "Win64"],
    navigatorProperties: {
        appName: ["Netscape"],
        appCodeName: ["Mozilla"],
        appVersion: [
            "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/110.0.0.0 Safari/537.36",
            "5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
        ],
        product: ["Gecko"],
        productSub: ["20030107"],
        vendor: ["Google Inc.", "Mozilla Foundation", "Microsoft Corporation"],
        vendorSub: [""]
    },
    canvasFingerprints: [
        "NoisyCanvasFingerprint1",
        "NoisyCanvasFingerprint2",
        "NoisyCanvasFingerprint3"
    ]
};

// Генератор случайных значений
function getRandomElement(array) {
    return array[Math.floor(Math.random() * array.length)];
}

// Проверка существующего пользовательского конфига
async function loadUserProfile() {
    try {
        const result = await browser.storage.local.get("userProfile");
        return result.userProfile || null;
    } catch (error) {
        console.error("Error loading user profile:", error);
        return null;
    }
}

// Сохранение пользовательского профиля
async function saveUserProfile(profile) {
    if (!browser.storage || !browser.storage.local) {
        console.error("browser.storage.local is not available. Check your manifest.json and ensure the script is running in the correct context.");
        return;
    }
    try {
        await browser.storage.local.set({ userProfile: profile });
        console.log("User profile saved to browser.storage.local:", profile);
    } catch (error) {
        console.error("Error saving user profile:", error);
    }
}

// Генерация WebGL параметров с выбором одного значения
function generateWebGLProfile(config) {
    const vendors = Object.keys(config.webGL);
    const selectedVendor = getRandomElement(vendors);
    const renderers = config.webGL[selectedVendor];
    
    // Выбираем случайный рендерер для выбранного вендора
    const selectedRenderer = Array.isArray(renderers) ? getRandomElement(renderers) : renderers;

    return {
        vendor: selectedVendor,
        renderer: selectedRenderer
    };
}

// Вставляем в основную функцию генерации профиля
function generateUserProfile(config) {
    const profile = {
        userAgents: getRandomElement(config.userAgents),
        screenResolutions: getRandomElement(config.screenResolutions),
        deviceMemories: getRandomElement(config.deviceMemories),
        hardwareConcurrencies: getRandomElement(config.hardwareConcurrencies),
        languages: getRandomElement(config.languages),
        platforms: getRandomElement(config.platforms),
        webGL: generateWebGLProfile(config), // Одно значение для WebGL
        canvasFingerprints: getRandomElement(config.canvasFingerprints)
    };

    console.log("Generated user profile:", profile);
    return profile;
}


// Проверка и дополнение существующего профиля
async function ensureUserProfile(config) {
    let profile = await loadUserProfile();
    if (profile) {
        console.log("Existing profile found:", profile);

        // Проверяем, есть ли пропущенные значения
        let updated = false;
        for (const [key, values] of Object.entries(config)) {
            if (!profile[key]) {
                if (Array.isArray(values) && values.length > 0) {
                    profile[key] = getRandomElement(values);
                    updated = true;
                } else if (typeof values === "object") {
                    profile[key] = {};
                    for (const [subKey, subValues] of Object.entries(values)) {
                        if (Array.isArray(subValues) && subValues.length > 0) {
                            profile[key][subKey] = getRandomElement(subValues);
                        }
                    }
                    updated = true;
                }
            }
        }
        if (updated) {
            await saveUserProfile(profile);
        } else {
            console.log("Profile is already complete.");
        }
    } else {
        console.log("No profile found. Generating a new one.");
        profile = generateUserProfile(config);
        await saveUserProfile(profile);
    }
    return profile;
}

// Применение пользовательского профиля
function applyUserProfile(profile) {
    const userAgent = profile.userAgents || getRandomElement(defaultUserAgents);

    // Перехват и подмена заголовков
    browser.webRequest.onBeforeSendHeaders.addListener(
        function (details) {
            const headers = details.requestHeaders.map((header) => {
                if (header.name.toLowerCase() === "user-agent") {
                    header.value = userAgent;
                }
                return header;
            });
            return { requestHeaders: headers };
        },
        { urls: ["<all_urls>"] },
        ["blocking", "requestHeaders"]
    );

    // Обработка webGL
    if (profile.webGL) {
        const webGLVendor = Object.keys(profile.webGL)[0] || "Google Inc.";
        const webGLRenderer = profile.webGL[webGLVendor][0] || "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)";

        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function (param) {
            if (param === this.VENDOR) {
                return webGLVendor;
            }
            if (param === this.RENDERER) {
                return webGLRenderer;
            }
            return getParameter.call(this, param);
        };
    }

    console.log("Applied user profile:", profile);
}

function overrideWebGLProfile(webGLProfile) {
    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;

    WebGLRenderingContext.prototype.getParameter = function (parameter) {
        if (parameter === this.VENDOR) {
            return webGLProfile.vendor; // Подменяем vendor
        }
        if (parameter === this.RENDERER) {
            return webGLProfile.renderer; // Подменяем renderer
        }
        return originalGetParameter.call(this, parameter);
    };

    console.log("WebGL profile overridden with:", webGLProfile);
}


// Основная логика аддона
(async function () {
    const config = generationConfig; // Используем встроенную конфигурацию
    const userProfile = await ensureUserProfile(config);
    applyUserProfile(userProfile);
    overrideWebGLProfile(userProfile.webGL); // Подмена WebGL
})();
