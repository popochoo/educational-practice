import unittest
from unittest.mock import patch, MagicMock
from main import calculate_material_required


class MockRow(dict):
    def __init__(self, data, key):
        super().__init__({key: data})
        self.data = data
        self.key = key

    def __getitem__(self, item):
        if isinstance(item, int) and item == 0:
            return self.data
        return super().__getitem__(item)


class TestMaterialCalculation(unittest.TestCase):

    @patch('main.get_db_connection')
    def test_standard_calculation(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.side_effect = [
            MockRow(1.05, "product_type_coefficient"),
            MockRow(0.50, "scrap_percentage")
        ]

        result = calculate_material_required(1, 1, 10, 1.5, 2.0)
        self.assertEqual(result, 32)

    @patch('main.get_db_connection')
    def test_ceil_rounding(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.side_effect = [
            MockRow(1.00, "product_type_coefficient"),
            MockRow(0.00, "scrap_percentage")
        ]

        result = calculate_material_required(1, 1, 10, 3.001, 1.0)
        self.assertEqual(result, 31)

    @patch('main.get_db_connection')
    def test_non_existent_type_id(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [None, None]

        result = calculate_material_required(999, 999, 10, 1.5, 2.0)
        self.assertEqual(result, -1)

    def test_negative_parameters(self):
        result_1 = calculate_material_required(1, 1, 10, -1.5, 2.0)
        result_2 = calculate_material_required(1, 1, 10, 1.5, -2.0)

        self.assertEqual(result_1, -1)
        self.assertEqual(result_2, -1)

    def test_zero_or_negative_quantity(self):
        result_zero = calculate_material_required(1, 1, 0, 1.5, 2.0)
        result_neg = calculate_material_required(1, 1, -10, 1.5, 2.0)

        self.assertEqual(result_zero, -1)
        self.assertEqual(result_neg, -1)


if __name__ == '__main__':
    unittest.main()