import logging
import time
from datetime import datetime

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from database import Habits, HabitTracking, Users
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import BOT_TOKEN, DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=False)

sql_logger = logging.getLogger("sqlalchemy.engine")
sql_logger.setLevel(logging.INFO)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
logger.info("scheduler: engine and SessionLocal initialized")

bot = telebot.TeleBot(BOT_TOKEN)
logger.info("scheduler: telebot initialized")

scheduler = BackgroundScheduler()
logger.info("scheduler: BackgroundScheduler created")


def send_notifications() -> None:
    """
    Отправляет напоминания пользователям о привычках с наступившим временем оповещения.

    Функция выполняет выборку из базы данных всех привычек, для которых время
    оповещения (`alert_time`) совпадает с текущим временем, и счётчик выполнений
    меньше 21, после чего отправляет пользователям сообщения в Telegram через бота.
    В случае ошибок при запросе к БД или отправке сообщений пишет подробные логи
    и не выбрасывает исключения наружу.
    """

    current_time = datetime.now().time().replace(second=0, microsecond=0)

    logger.info(
        "send_notifications: tick at %s",
        current_time.strftime("%H:%M"),
    )

    try:
        with SessionLocal() as session:
            statement = (
                select(Users.telegram_id, Habits.habit_name)
                .join(Habits, Habits.user_id == Users.id)
                .join(HabitTracking, HabitTracking.habits_id == Habits.id)
                .where(
                    HabitTracking.alert_time == current_time, HabitTracking.count < 21
                )
            )
            rows = session.execute(statement).all()

    except Exception as exc:
        logger.exception(
            "send_notifications: DB query failed at %s, error=%r",
            current_time,
            exc,
        )
        return

    logger.info(
        "send_notifications: found %s notifications to send at %s",
        len(rows),
        current_time.strftime("%H:%M"),
    )

    for telegram_id, habit_name in rows:
        try:
            logger.debug(
                "send_notifications: sending reminder to telegram_id=%s, habit_name=%r",
                telegram_id,
                habit_name,
            )
            bot.send_message(telegram_id, f"Пора выполнить привычку: {habit_name}")
        except Exception as exc:
            logger.exception(
                "send_notifications: failed to send to telegram_id=%s, error=%r",
                telegram_id,
                exc,
            )


def start_scheduler() -> None:
    """
    Запускает планировщик напоминаний и удерживает процесс в рабочем состоянии.

    Регистрирует задачу `send_notifications` в планировщике APScheduler с
    периодичностью в одну минуту, запускает планировщик и блокирует поток
    в бесконечном цикле. Корректно останавливает планировщик при получении
    `KeyboardInterrupt` или при возникновении непредвидённой ошибки, записывая
    информацию о запуске, остановке и ошибках в логи.
    """

    logger.info("start_scheduler: registering job send_notifications every 1 minute")
    scheduler.add_job(send_notifications, "interval", minutes=1)
    scheduler.start()
    logger.info("start_scheduler: scheduler started")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(
            "start_scheduler: KeyboardInterrupt received, shutting down scheduler"
        )
        scheduler.shutdown()
        logger.info("start_scheduler: scheduler stopped")
    except Exception as exc:
        logger.exception("start_scheduler: unexpected error, shutting down: %r", exc)
        scheduler.shutdown()
