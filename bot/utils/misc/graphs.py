from typing import List, Tuple

import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from io import BytesIO
from numpy import ndarray
import random


def generate_date_range(habits_data) -> Tuple[datetime, datetime, List[datetime]]:
    all_dates = []
    for habit in habits_data:
        for check in habit['habit_tracking_statistics']:
            dt_str = check['completion_date']
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            all_dates.append(dt)

    # сортируем
    date_sort = sorted(all_dates) if all_dates else [datetime.now()]
    min_date = date_sort[0] - timedelta(days=1) if all_dates else datetime.now() - timedelta(days=1)
    max_date = date_sort[-1] + timedelta(days=1) if all_dates else datetime.now() + timedelta(days=1)
    date_ticks = []

    current_date = date_sort[0]
    while current_date < date_sort[-1]:
        date_ticks.append(current_date)
        current_date += timedelta(days=1)

    return min_date, max_date, date_ticks


def get_graphs_habits(data):
    habits = data
    n_habits = len(habits)

    # записываем все даты
    min_date, max_date, date_ticks = generate_date_range(habits_data=habits)

    # Создаем график в памяти
    fig, axes = plt.subplots(nrows=n_habits, ncols=1, figsize=(14, 4 * n_habits))

    if n_habits == 1:
        axes = [axes]

    # генерируем цвета для точек на графике
    colors: List[str] = [f"#{random.randint(0, 0xFFFFFF):06X}" for _ in range(n_habits)]

    for idx, habit in enumerate(habits):
        habit_name: str = habit['habit_name']
        check_dates: str = habit['habit_tracking_statistics']

        ax = axes[idx]

        if len(check_dates) > 0:
            dates = []
            times = []

            # Извлекаем даты и времена для этой привычки
            for check in check_dates:
                dt_str = check['completion_date']
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

                dates.append(dt)
                time_hours = dt.hour + dt.minute / 60.0
                times.append(time_hours)

            # === СТАВИМ ТОЛЬКО НАШИ ТОЧКИ ===
            dates_sorted = sorted(dates)
            times_sorted = [times[dates.index(d)] for d in dates_sorted]

            ax.scatter(dates_sorted, times_sorted,
                       s=150, c=colors[idx], alpha=0.7,
                       marker='o', edgecolors='black', linewidths=1)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            ax.set_xticks(date_ticks)
            ax.set_xlim(min_date, max_date)

            ax.set_xlabel('Дата', fontsize=11)

            ax.set_ylim(0, 24)
            ax.set_yticks([0, 3, 6, 9, 12, 15, 18, 21, 24])
            ax.set_yticklabels(['00:00', '03:00', '06:00', '09:00', '12:00',
                                '15:00', '18:00', '21:00', '24:00'])
            ax.set_ylabel('Время выполнения', fontsize=11)

            ax.set_title(f'{habit_name} — всего выполнений: {len(check_dates)}',
                         fontsize=12, fontweight='bold')

            ax.axhspan(6, 12, alpha=0.1, color='orange')
            ax.axhspan(12, 18, alpha=0.1, color='green')
            ax.axhspan(18, 22, alpha=0.1, color='blue')
            ax.axhspan(22, 24, alpha=0.1, color='purple')
            ax.axhspan(0, 6, alpha=0.1, color='purple')

            ax.grid(True, alpha=0.3)
            # if len(dates_sorted) == 1:
            #     # Если только 1 дата, добавляем +/- 1 день для диапазона
            #     single_date = dates_sorted[0]
            #     ax.set_xlim(single_date - timedelta(days=1),
            #                 single_date + timedelta(days=1))
            # else:
            #     # Если несколько дат, автоматически подстраиваем с небольшим запасом
            #     ax.set_xlim(dates_sorted[0] - timedelta(days=0.5),
            #                 dates_sorted[-1] + timedelta(days=0.5))
            # Улучшаем читаемость дат — поворачиваем текст
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'Нет выполнений', transform=ax.transAxes,
                    ha='center', va='center', fontsize=14, color='gray')
            ax.set_title(f'{habit_name} — всего выполнений: 0',
                         fontsize=12, fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 24)

    fig.suptitle('Статистика: время выполнения привычек по датам',
                 fontsize=16, fontweight='bold', y=1.02)

    plt.tight_layout()

    # Сохраняем в BytesIO (в память, не в файл)
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)  # Возвращаем курсор в начало
    plt.close()  # Закрываем график

    return img_buffer
