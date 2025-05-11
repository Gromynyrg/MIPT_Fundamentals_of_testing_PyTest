import uuid


MOCKED_AVAILABLE_SEATS_DB = {
    "1001": 50,
    "1002": 0,
    "1003": 5,
    "1999": 1000
}


MOCKED_PROMO_CODES_DB = {
    "VALID10": {"active": True, "discount_value": 0.10, "uses_left": 5},
    "EXPIRED50": {"active": False, "discount_value": 0.50, "uses_left": 100},
    "USEDUP": {"active": True, "discount_value": 0.20, "uses_left": 0},
    "SUPERDEAL": {"active": True, "discount_value": 0.90, "uses_left": 1}
}


def calc_price(base_price: float, discount: float, count: int) -> float:
    """
    Функция рассчитывает итоговую сумму за count билетов с учетом базовой цены и возможной скидки.

    :param base_price: Базовая цена билета
    :param discount: Скидка в процентах
    :param count: Количество билетов
    :return: Итоговая сумма за билеты
    """
    if not isinstance(base_price, (int, float)) or not isinstance(discount, (int, float)):
        raise TypeError("Базовая цена и скидка должны быть числами.")
    if not isinstance(count, int):
        raise TypeError("Количество билетов должно быть целым числом.")

    if base_price < 0:
        raise ValueError("Базовая цена не может быть отрицательной.")
    if not 0 <= discount <= 1:
        raise ValueError("Скидка должна быть в диапазоне от 0 до 1.")
    if count < 0:
        raise ValueError("Количество билетов не может быть отрицательным.")

    if count == 0:
        return 0.0

    final_price = base_price * (1 - discount) * count
    return round(final_price, 2)


def check_availability(event_id: int, seats_requested: int) -> bool:
    """
    Функция проверяет доступность мест на мероприятии.

    :param event_id: Идентификатор мероприятия
    :param seats_requested: Запрашиваемое количество мест
    :return: True, если места доступны, иначе False
    """
    if not isinstance(event_id, int) or not isinstance(seats_requested, int):
        raise TypeError("ID события и количество запрашиваемых мест должны быть целыми числами.")

    if seats_requested <= 0:
        return False

    available_seats = MOCKED_AVAILABLE_SEATS_DB.get(str(event_id), 0)
    return available_seats >= seats_requested


def apply_promo_code(order_id: int, promo_code: str) -> bool:
    """
    Функция применяет промокод к заказу.

    :param order_id: Идентификатор заказа
    :param promo_code: Промокод
    :return: True, если промокод применен успешно, иначе False
    """
    if not isinstance(order_id, int) or not isinstance(promo_code, str):
        raise TypeError("ID заказа должен быть целым числом, а промокод - строкой.")

    promo_data = MOCKED_PROMO_CODES_DB.get(promo_code)

    if promo_data is None or not promo_data["active"] or promo_data["uses_left"] <= 0:
        return False

    promo_data["uses_left"] -= 1
    return True


def generate_booking_ref(user_id: int, event_id: int) -> str:
    """
    Функция генерирует уникальный код/референс бронирования на основе идентификаторов пользователя и события.

    :param user_id: Идентификатор пользователя
    :param event_id: Идентификатор мероприятия
    :return: Уникальный идентификатор бронирования
    """
    if not isinstance(user_id, int) or not isinstance(event_id, int):
        raise TypeError("ID пользователя и ID события должны быть целыми числами.")
    if user_id <= 0 or event_id <= 0:
        raise ValueError("ID пользователя и ID события должны быть положительными числами.")

    generate_uniq = uuid.uuid4().hex[:8].upper()
    return f"BOOK-{user_id}-{event_id}-{generate_uniq}"


def send_notification_email(email: str, booking_details: dict) -> bool:
    """
    Функция отправляет уведомление на почту при успешном бронировании/оплате.

    :param email: Адрес электронной почты
    :param booking_details: Детали бронирования
    :return: True, если уведомление успешно отправлено, иначе False
    """
    if not isinstance(email, str) or "@" not in email or "." not in email.split('@')[-1]:
        return False

    if not isinstance(booking_details, dict) or not booking_details:
        return False

    print(f"Имитация отправки письма на {email} с деталями: {booking_details}")

    if email == "fail@example.com":
        return False

    return True
