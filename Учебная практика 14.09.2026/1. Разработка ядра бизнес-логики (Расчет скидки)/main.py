def calculate_partner_discount(total_quantity: int) -> int:
    if total_quantity < 10000:
        return 0
    if total_quantity < 50000:
        return 5
    if total_quantity < 300000:
        return 10
    return 15


def run_tests():
    assert calculate_partner_discount(9999) == 0

    assert calculate_partner_discount(10000) == 5
    assert calculate_partner_discount(49999) == 5

    assert calculate_partner_discount(50000) == 10
    assert calculate_partner_discount(299999) == 10

    assert calculate_partner_discount(300000) == 15

    print("Все тесты успешно пройдены! Покрытие 100%.")


if __name__ == "__main__":
    run_tests()
