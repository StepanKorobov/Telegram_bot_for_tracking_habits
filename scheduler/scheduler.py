from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL, BOT_TOKEN
# scheduler/scheduler.py
from datetime import datetime
import time

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from database import Users, Habits, HabitTracking

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

bot = telebot.TeleBot(BOT_TOKEN)

scheduler = BackgroundScheduler()


def send_notifications():
    current_time = datetime.now().time().replace(second=0, microsecond=0)

    with SessionLocal() as session:
        statement = (
            select(Users.telegram_id, Habits.habit_name)
            .join(Habits, Habits.user_id == Users.id)
            .join(HabitTracking, HabitTracking.habits_id == Habits.id)
            .where(HabitTracking.alert_time == current_time, HabitTracking.count < 21)
        )
        rows = session.execute(statement).all()

    for telegram_id, habit_name in rows:
        bot.send_message(telegram_id, f"Пора выполнить привычку: {habit_name}")


def start_scheduler():
    scheduler.add_job(send_notifications, "interval", minutes=1)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
