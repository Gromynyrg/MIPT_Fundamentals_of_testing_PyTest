import pytest
from services.booking_functions import *


@pytest.mark.parametrize(
    "base_price, discount, count, expected_cost",
    [
        (100.0, 0.1, 2, 180.0),
        (50.0, 0.0, 1, 50.0),
        (200.0, 1.0, 3, 0.0),
        (10.0, 0.25, 0, 0.0),
        (123.45, 0.15, 1, 104.93)
    ]
)
def test_calc_booking_cost_positive(base_price, discount, count, expected_cost):
    """
    Функция для проверки вычисления стоимости бронирования для различных входных данных.
    ПОЗИТИВНЫЕ КЕЙСЫ

    :param base_price: Базовая цена билета
    :param discount: Скидка в процентах
    :param count: Количество билетов
    :param expected_cost: Ожидаемая стоимость бронирования
    """
    assert calc_price(base_price, discount, count) == pytest.approx(expected_cost)


@pytest.mark.parametrize(
    "base_price, discount, count, expected_exception, error_message",
    [
        (-100.0, 0.1, 2, ValueError, "Базовая цена не может быть отрицательной"),
        (100.0, 1.1, 2, ValueError, "Скидка должна быть в диапазоне от 0 до 1"),
        (100.0, -0.1, 2, ValueError, "Скидка должна быть в диапазоне от 0 до 1"),
        (100.0, 0.1, -2, ValueError, "Количество билетов не может быть отрицательным"),
        (100, 0.1, "2", TypeError, "Количество билетов должно быть целым числом"),
    ]
)
def test_calc_booking_cost_negative(base_price, discount, count, expected_exception, error_message):
    """
    Функция для проверки вычисления стоимости бронирования для различных входных данных.
    ПОЗИТИВНЫЕ КЕЙСЫ

    :param base_price: Базовая цена билета
    :param discount: Скидка в процентах
    :param count: Количество билетов
    :param expected_exception: Ожидаемое исключение
    :param error_message: Часть текста ошибки, которую ожидаем в сообщении исключения
    """
    with pytest.raises(expected_exception) as exception_info:
        calc_price(base_price, discount, count)
    assert error_message in str(exception_info.value)


@pytest.mark.parametrize(
    "event_id, seats_requested, expected_result, mock_db_state",
    [
        (1001, 10, True, {'1001': 50}),
        (1001, 50, True, {'1001': 50}),
        (1999, 1, True, {'1999': 1}),
    ]
)
def test_check_availability_positive(mocker, event_id, seats_requested, expected_result, mock_db_state):
    """
    Функция для проверки доступности мест для бронирования.

    :param mocker: Фикстура для мокирования объектов.
    :param event_id: Идентификатор события.
    :param seats_requested: Количество запрашиваемых мест.
    :param expected_result: Ожидаемый результат (True или False).
    :param mock_db_state: Состояние базы данных для мокирования.
    """
    mocker.patch.dict(MOCKED_AVAILABLE_SEATS_DB, mock_db_state, clear=True)
    assert check_availability(event_id, seats_requested) == expected_result


@pytest.mark.parametrize(
    "event_id, seats_requested, expected_result, mock_db_state, expected_exception, error_message_part",
    [
        (1001, 60, False, {'1001': 50}, None, None),
        (1002, 1, False, {'1002': 0}, None, None),
        (888, 10, False, {'1001': 50}, None, None),
        (1001, 0, False, {'1001': 50}, None, None),
        (1001, -5, False, {'1001': 50}, None, None),
        ("abc", 10, False, {}, TypeError, "ID события и количество запрашиваемых мест должны быть целыми числами."),
        (1001, "xyz", False, {}, TypeError, "ID события и количество запрашиваемых мест должны быть целыми числами."),
    ]
)
def test_check_availability_negative(mocker, event_id, seats_requested, expected_result, mock_db_state,
                                     expected_exception, error_message_part):
    """
    Функция для проверки доступности мест для бронирования с негативными тестами.

    :param mocker: Фикстура для мокирования объектов.
    :param event_id: Идентификатор события.
    :param seats_requested: Количество запрашиваемых мест.
    :param expected_result: Ожидаемый результат (True или False).
    :param mock_db_state: Состояние базы данных для мокирования.
    :param expected_exception: Ожидаемое исключение (если есть).
    :param error_message_part: Часть текста ошибки, которую ожидаем в сообщении исключения (если есть).
    """
    mocker.patch.dict(MOCKED_AVAILABLE_SEATS_DB, mock_db_state, clear=True)
    if expected_exception:
        with pytest.raises(expected_exception) as excinfo:
            check_availability(event_id, seats_requested)
        assert error_message_part in str(excinfo.value)
    else:
        assert check_availability(event_id, seats_requested) == expected_result
        
        
@pytest.fixture
def fresh_promo_codes_db(mocker):
    """
    Фикстура для предоставления "чистого" состояния MOCKED_PROMO_CODES_DB
    и его восстановления после теста.
    """
    initial_db_state = {
        "VALID10": {"active": True, "discount_value": 0.10, "uses_left": 5},
        "EXPIRED50": {"active": False, "discount_value": 0.50, "uses_left": 100},
        "USEDUP": {"active": True, "discount_value": 0.20, "uses_left": 0},
        "SUPERDEAL": {"active": True, "discount_value": 0.90, "uses_left": 1}
    }
    patcher = mocker.patch.dict(MOCKED_PROMO_CODES_DB, initial_db_state, clear=True)
    yield patcher


@pytest.mark.parametrize(
    "order_id, promo_code, expected_success",
    [
        (100, "VALID10", True),
        (200, "SUPERDEAL", True),
    ]
)
def test_apply_promo_code_positive(fresh_promo_codes_db, order_id, promo_code, expected_success):
    """
    Позитивные тесты для apply_promo_code.
    Используем фикстуру fresh_promo_codes_db для изоляции состояния.
    """
    success = apply_promo_code(order_id, promo_code)
    assert success == expected_success


@pytest.mark.parametrize(
    "order_id, promo_code, expected_success, expected_exception, error_message_part",
    [
        (100, "INVALIDCODE", False, None, None),
        (100, "EXPIRED50", False, None, None),
        (100, "USEDUP", False, None, None),
        (100, 123, False, TypeError, "ID заказа должен быть целым числом, а промокод - строкой.")
    ]
)
def test_apply_promo_code_negative(fresh_promo_codes_db, order_id, promo_code, expected_success,
                                   expected_exception, error_message_part):
    """
    Негативные тесты для apply_promo_code.
    """
    if expected_exception:
        with pytest.raises(expected_exception) as exception_data:
            apply_promo_code(order_id, promo_code)
        assert error_message_part in str(exception_data.value)
    else:
        success = apply_promo_code(order_id, promo_code)
        assert success == expected_success
        

@pytest.mark.parametrize(
    "user_id, event_id",
    [
        (1, 101),   # Позитивный: стандартные ID
        (9999, 8888) # Позитивный: другие ID
    ]
)
def test_generate_booking_ref_positive_format(user_id, event_id):
    """
    Позитивный тест: проверяем формат сгенерированного референса.
    """
    ref = generate_booking_ref(user_id, event_id)
    assert isinstance(ref, str)
    parts = ref.split('-')
    assert parts[0] == "BOOK"
    assert parts[1] == str(user_id)
    assert parts[2] == str(event_id)
    assert len(parts[3]) == 8
    assert parts[3].isalnum()


@pytest.mark.parametrize(
    "user_id, event_id, expected_exception, error_message_part",
    [
        (-1, 101, ValueError, "ID пользователя и ID события должны быть положительными числами."),
        (1, -101, ValueError, "ID пользователя и ID события должны быть положительными числами."),
        (0, 101, ValueError, "ID пользователя и ID события должны быть положительными числами."),
        (1, 0, ValueError, "ID пользователя и ID события должны быть положительными числами."),
        ("abc", 101, TypeError, "ID пользователя и ID события должны быть целыми числами."),
        (1, "xyz", TypeError, "ID пользователя и ID события должны быть целыми числами."),
    ]
)
def test_generate_booking_ref_negative(user_id, event_id, expected_exception, error_message_part):
    """
    Негативные тесты для generate_booking_ref.
    """
    with pytest.raises(expected_exception) as exception_data:
        generate_booking_ref(user_id, event_id)
    assert error_message_part in str(exception_data.value)


@pytest.fixture
def sample_booking_details():
    return {"event_name": "Концерт Рок-звезды", "tickets": 2, "total_price": 200.0}


@pytest.mark.parametrize(
    "email",
    [
        "test@example.com",
        "another.user@domain.co.uk"
    ]
)
def test_send_notification_email_positive(mocker, email, sample_booking_details):
    """
    Позитивные тесты для send_notification_email.
    Проверяем, что функция возвращает True при "успешной" отправке.
    Мы также можем проверить, что print (имитация отправки) был вызван.
    """
    mock_print = mocker.patch('builtins.print')

    result = send_notification_email(email, sample_booking_details)
    assert result is True
    mock_print.assert_any_call(f"Имитация отправки письма на {email} с деталями: {sample_booking_details}")


@pytest.mark.parametrize(
    "email, booking_details, expected_return, mock_smtp_exception, error_message_part",
    [
        ("invalid_email", {"id": 1}, False, None, None),
        ("", {"id": 1}, False, None, None),
        ("test@example.com", {}, False, None, None),
        ("fail@example.com", {"id": 123}, False, None, None),
    ]
)
def test_send_notification_email_negative(mocker, email, booking_details, expected_return, mock_smtp_exception,
                                          error_message_part):
    """
    Негативные тесты для send_notification_email.
    """
    mock_print = mocker.patch('builtins.print')

    result = send_notification_email(email, booking_details)
    assert result == expected_return
