"""Calculator app calculations processing."""
from collections import namedtuple
import decimal
import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class UserInputHandler:
    """Parse and prepare user input for further calculations."""

    def __init__(self, user_inputs: list[Decimal]):
        self.user_inputs = user_inputs
        self.percent_values = []
        self.sum_values = []

    def append_list(self, field: str, value) -> None:
        """Append lists of percent and non-percent values."""
        try:
            decimal_value = round(Decimal(value), 2)
        except InvalidOperation:
            logger.info(f"Invalid input for field '{field}': {value}")
            return

        if 'percent' in field:  # Check for percentage values.
            self.percent_values.append(decimal_value)
        else:
            self.sum_values.append(decimal_value)  # Append non-percent values.

    def parse_user_input(self) -> tuple:
        """Returns tuple with separated lists of percent and non-percent values."""

        for field, value in self.user_inputs.items():
            if field == "other_fields":
                if not isinstance(value, list):
                    raise TypeError("Expected a list for 'other_fields'")
                for item in value:
                    if not isinstance(item, dict):
                        raise TypeError("Expected a dictionary in 'other_fields' list")
                    field_name = item.get('field_name')
                    field_value = item.get('value')
                    if not isinstance(field_name, str):
                        raise TypeError("Invalid type for field_name, expected string.")
                    if not isinstance(field_value, Decimal):
                        raise TypeError("Invalid type for field_value, expected Decimal.")
                    self.append_list(field_name, field_value)
            else:
                if 'margin_percent' != field:
                    self.append_list(field, value)

        lists = namedtuple('lists', ['sum_values', 'percent_values'])
        output = lists(sum_values=self.sum_values,
                       percent_values=self.percent_values)
        return output


class Calculator:
    """Functionality for calculations."""

    def __init__(self, sum_values: list, percent_values: list, user_input: dict) -> None:
        self.sum_values = sum_values
        self.percent_values = percent_values
        self.user_input = user_input

    def get_total_expenses(self) -> decimal:
        """Calculate total expenses."""

        summ_of_inputs = sum(self.sum_values)
        result = summ_of_inputs

        if self.percent_values:
            for value in self.percent_values:
                result += summ_of_inputs * (value / 100)
        rounded_result = round(Decimal(result), 2)

        return rounded_result

    def get_recommended_price(self, total_expenses: Decimal) -> Decimal:
        """Returns recommended price according to user margin input and expenses."""

        margin = Decimal(self.user_input.get('margin_percent', Decimal(0)))
        recommended_price = Decimal(
            total_expenses + total_expenses * (margin / 100))
        rounded_recommended_price = round(recommended_price, 2)
        return rounded_recommended_price

    @staticmethod
    def get_net_profit(total_expenses: Decimal, recommended_price: Decimal) -> Decimal:
        """Returns estimated net profit."""

        net_profit = round((recommended_price - total_expenses), 2)
        return net_profit
