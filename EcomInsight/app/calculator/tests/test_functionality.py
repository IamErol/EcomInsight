from decimal import Decimal
from django.test import TestCase
from calculator.services import UserInputHandler, Calculator


class UserInputHandlerTest(TestCase):
    """ Test for UserInputHandler. """

    def test_separate_inputs_to_lists(self):
        """ Test separate inputs into sum list and percent list. """
        data = {
            "other_fields": [
                {"field_name": "percent_value", "value": 5},
                {"field_name": "percent_value", "value": 50},
                {"field_name": "sum_value", "value": 15.0},
                {"field_name": "sum_value", "value": 25.0}
            ],
            "margin_percent": 100,
            "buying_price": 10.0,
            "transportation": 50.0,
            "packaging": 60.0,
            "warehouse": 70.0,
            "marketplace_comission_percent": -10.05
        }

        handler = UserInputHandler(data)

        percent_list = [Decimal('5.00'), Decimal('50.00'), Decimal('10.05')]
        sum_list = [Decimal('15.00'), Decimal('25.00'), Decimal('10.00'),
                    Decimal('50.00'), Decimal('60.00'), Decimal('70.00')]
        output = handler.parse_user_input()
        sum_list_output = output.sum_values
        percent_list_output = output.percent_values

        self.assertListEqual(percent_list, percent_list_output)
        self.assertListEqual(sum_list, sum_list_output)

    def test_empty_input_data(self):
        """ Test handling of empty input data. """
        data = {}
        handler = UserInputHandler(data)

        output = handler.parse_user_input()
        self.assertListEqual([], output.sum_values)
        self.assertListEqual([], output.percent_values)

    def test_invalid_data_types(self):
        """ Test handling of invalid data types. """
        data = {"other_fields": [{"field_name": "percent_value", "value": "invalid"}]}
        handler = UserInputHandler(data)

        with self.assertRaises(TypeError):
            handler.parse_user_input()

    def test_negative_sum_values(self):
        """ Test handling of negative sum values. """
        data = {"other_fields": [{"field_name": "sum_value", "value": -20.0}]}
        handler = UserInputHandler(data)

        output = handler.parse_user_input()
        self.assertIn(Decimal('-20.00'), output.sum_values)

    def test_unusual_field_names(self):
        """ Test handling of unusual field names. """
        data = {"other_fields": [{"field_name": "unexpected_field", "value": 30.0}]}
        handler = UserInputHandler(data)

        output = handler.parse_user_input()
        self.assertListEqual([Decimal('30.00')],
                             output.sum_values)  # Assuming all non-percent fields are treated as sum values


class CalculationsTest(TestCase):
    """ Test for Calculator. Expenses, recommended price, and net profit calculations. """

    def test_expences_calculation(self):
        """ Test calculation of total expenses. """
        sum_list = [Decimal('10.5879'), Decimal('10.0'), Decimal('10'),
                    Decimal('50'), Decimal('-50'), Decimal('70')]
        percent_list = [Decimal('5'), Decimal('10.58')]
        data = {"margin_percent": 100}

        calculator = Calculator(sum_values=sum_list, percent_values=percent_list, user_input=data)
        total_expenses = calculator.get_total_expenses()
        self.assertEqual(total_expenses, Decimal('116.26'))

    def test_calculate_recommended_price(self):
        """ Test calculation of recommended price. """
        data = {"margin_percent": 10}
        total_expenses = Decimal('142.08')
        calculator = Calculator(sum_values=[], percent_values=[], user_input=data)

        recommended_price = calculator.get_recommended_price(total_expenses=total_expenses)
        self.assertEqual(recommended_price, Decimal('156.29'))

    def test_expenses_with_no_percent_values(self):
        """ Test calculation of total expenses with no percent values. """
        sum_list = [Decimal('100'), Decimal('200')]
        percent_list = []
        data = {"margin_percent": 20}

        calculator = Calculator(sum_values=sum_list, percent_values=percent_list, user_input=data)
        total_expenses = calculator.get_total_expenses()
        self.assertEqual(total_expenses, Decimal('300.00'))

    def test_expenses_with_no_sum_values(self):
        """ Test calculation of total expenses with no sum values. """
        sum_list = []
        percent_list = [Decimal('10')]
        data = {"margin_percent": 15}

        calculator = Calculator(sum_values=sum_list, percent_values=percent_list, user_input=data)
        total_expenses = calculator.get_total_expenses()
        self.assertEqual(total_expenses, Decimal('0.00'))

    def test_empty_lists(self):
        """ Test calculation with empty sum and percent lists. """
        sum_list = []
        percent_list = []
        data = {"margin_percent": 10}

        calculator = Calculator(sum_values=sum_list, percent_values=percent_list, user_input=data)
        total_expenses = calculator.get_total_expenses()
        self.assertEqual(total_expenses, Decimal('0.00'))

    def test_negative_margin_price_calculation(self):
        """ Test calculation of recommended price with negative margin. """
        data = {"margin_percent": -10}
        total_expenses = Decimal('100')
        calculator = Calculator(sum_values=[], percent_values=[], user_input=data)

        recommended_price = calculator.get_recommended_price(total_expenses=total_expenses)
        self.assertEqual(recommended_price, Decimal('90.00'))

    def test_net_profit_calculation(self):
        """ Test calculation of net profit. """
        data = {"margin_percent": 25}
        total_expenses = Decimal('100')
        recommended_price = Decimal('125')
        calculator = Calculator(sum_values=[], percent_values=[], user_input=data)

        net_profit = calculator.get_net_profit(total_expenses=total_expenses, recommended_price=recommended_price)
        self.assertEqual(net_profit, Decimal('25.00'))
