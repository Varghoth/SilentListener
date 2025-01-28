const axios = require("axios");

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

if (!BOT_TOKEN || !CHAT_ID) {
  console.error("❌ Ошибка: не установлены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID!");
  process.exit(1);
}

/**
 * Отправляет уведомление в Telegram
 * @param {string} message - Текст уведомления
 */
async function sendNotification(message) {
  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  const data = {
    chat_id: CHAT_ID,
    text: message,
  };

  try {
    const response = await axios.post(url, data);
    console.log("✅ Уведомление отправлено в Telegram:", response.data);
  } catch (error) {
    console.error("❌ Ошибка при отправке уведомления:", error.response ? error.response.data : error.message);
  }
}

/**
 * Обрабатывает входящий HTTP-запрос о статусе контейнера
 */
exports.handleStatus = async (req, res) => {
  console.log("📩 Получен запрос:", req.body);

  const { container_id, status } = req.body;

  if (!container_id || !status) {
    console.error("❌ Некорректный payload");
    return res.status(400).json({ error: "Invalid payload" });
  }

  try {
    if (status === "TemplatePauseMissing") {
      const message = `⚠️ Проблема в контейнере ${container_id}: Pause не найден 3 раза подряд`;
      await sendNotification(message);
    }

    res.status(200).json({ message: "Статус обработан успешно" });
  } catch (error) {
    console.error("❌ Ошибка обработки запроса:", error.message);
    res.status(500).json({ error: "Internal Server Error" });
  }
};
