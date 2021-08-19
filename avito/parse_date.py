def parse_date(item: str):
    params = item.strip().split(' ')
    # print(params)
    if len(params) == 2:
        day, time = params
        if day == 'Сегодня':
            date = datetime.date.today()
        elif day == 'Вчера':
            date = datetime.date.today() - datetime.timedelta(days=1)
        else:
            print('Не смогли разобрать день:', item)
            return

        time = datetime.datetime.strptime(time, '%H:%M').time()
        return datetime.datetime.combine(date=date, time=time)

    elif len(params) == 3:
        day, month_hru, time = params
        day = int(day)
        months_map = {
            'января': 1,
            'февраля': 2,
            'марта': 3,
            'апреля': 4,
            'мая': 5,
            'июня': 6,
            'июля': 7,
            'августа': 8,
            'сентября': 9,
            'октября': 10,
            'ноября': 11,
            'декабря': 12,
        }
        month = months_map.get(month_hru)
        if not month:
            print('Не смогли разобрать месяц:', item)
            return
        
        today = datetime.datetime.today()
        time = datetime.datetime.strptime(time, '%H:%M')
        return datetime.datetime(day=day, month=month, year=today.year, hour=today.hour, minute=time.minute)

    else:
        print('Не смогли разобрать формат:', item)
        return