from celery_app import app, bot
import time


@app.task(bind=True, name="send_notification")
def send_notification(self, user_id: int, message: str):
    # bind=True даёт доступ к self — можно делать retry, логировать и т.д.
    print(f"[TASK] Отправка уведомления пользователю {user_id}: {message}")
    time.sleep(2)  # имитация работы
    return {"user_id": user_id, "message": message, "status": "sent"}


@app.task(name="add_numbers")
def add_numbers(x: int, y: int):
    result = sum([x ** 10 for x in range(100000000)])
    bot.send_message(
        chat_id=1867915977,
        text="1000000 ** 10",
    )
    return result
