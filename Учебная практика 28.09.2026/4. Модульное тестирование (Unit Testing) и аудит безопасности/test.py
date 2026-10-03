import unittest
from unittest.mock import patch
# Импортируем метод расчета из вашего основного файла
from main import calculate_material_required


class TestMaterialCalculation(unittest.TestCase):

    # ТЕСТ 1: Проверка обычного корректного расчета с известным результатом
    @patch('main.get_db_connection')
    def test_standard_calculation(self, mock_db):
        # Настраиваем мок-ответы для коэффициента (1.05) и брака (0.50%)
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [(1.05,), (0.50,)]

        # Выполняем расчет: 1.5 * 2.0 * 1.05 * 10 * (1 + 0.5/100) = 31.6575
        result = calculate_material_required(1, 1, 10, 1.5, 2.0)
        self.assertEqual(result, 32)

    # ТЕСТ 2: Проверка, что дробный результат округляется строго в большую сторону (ceil)
    @patch('main.get_db_connection')
    def test_ceil_rounding(self, mock_db):
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [(1.00,), (0.00,)]

        # Расчет дает ровно 30.01. С округлением вверх (ceil) должно получиться 31
        result = calculate_material_required(1, 1, 10, 3.001, 1.0)
        self.assertEqual(result, 31)

    # ТЕСТ 3: Проверка возврата -1 при передаче некорректных/несуществующих ID типов
    @patch('main.get_db_connection')
    def test_non_existent_type_id(self, mock_db):
        mock_conn = mock_db.return_value
        mock_cursor = mock_conn.cursor.return_value
        # Имитируем, что база данных не нашла записи и вернула None
        mock_cursor.fetchone.side_effect = [None, None]

        result = calculate_material_required(999, 999, 10, 1.5, 2.0)
        self.assertEqual(result, -1)

    # ТЕСТ 4: Проверка возврата -1 при передаче отрицательных размеров параметров
    def test_negative_parameters(self):
        # Передаем отрицательный param_1 (-1.5)
        result_1 = calculate_material_required(1, 1, 10, -1.5, 2.0)
        # Передаем отрицательный param_2 (-2.0)
        result_2 = calculate_material_required(1, 1, 10, 1.5, -2.0)

        self.assertEqual(result_1, -1)
        self.assertEqual(result_2, -1)

    # ТЕСТ 5: Проверка возврата -1, если количество продукции равно нулю или меньше
    def test_zero_or_negative_quantity(self):
        # Передаем нулевое количество (0)
        result_zero = calculate_material_required(1, 1, 0, 1.5, 2.0)
        # Передаем отрицательное количество (-10)
        result_neg = calculate_material_required(1, 1, -10, 1.5, 2.0)

        self.assertEqual(result_zero, -1)
        self.assertEqual(result_neg, -1)


if __name__ == '__main__':
    unittest.main()