import locale

from .country import Country

def format_currency(number, country_code=None, currency_code=None, currency_symbol=None, decimal_separator=None, thousands_separator=None, use_current_locale=False, **kwargs):
    """
    Formats a given number as a currency string according to various parameters and optional locale settings.
    
    Parameters:
    - number (float): The numerical value to be formatted.
    - country_code (str, optional): The country code to determine currency formatting rules. Defaults to None.
    - currency_code (str, optional): The currency code to determine currency formatting rules. Defaults to None.
    - currency_symbol (str, optional): The symbol to be used for the currency. Defaults to None.
    - decimal_separator (str, optional): The character to use as a decimal separator. Defaults to None.
    - thousands_separator (str, optional): The character to use as a thousands separator. Defaults to None.
    - use_current_locale (bool, optional): Whether to use the current locale settings for formatting. Defaults to False.
    - kwargs (dict): Additional keyword arguments.
    
    Allowed kwargs:
    - place_currency_symbol_at_end (bool): Whether to place the currency symbol at the end of the formatted number. Default is false.
    - decimal_places (int): The number of decimal places to display. Uses decimal places according to country if no provided, and defaults to 2 if country_code or currency_code not provided.
    - number_format_system (str): Number format system you want to use. Defaults to `auto`. Supported number format systems are 
        - `global` or `international` i.e. "International Number System"
        - `indian` i.e. "Indian Number System"
        - `chinese` i.e. "Chinese Number System"
        - `auto` i.e. "Auto Format" (based on the country i.e. from `country_code` or `currency_code`)
        - `none` i.e. "No Formatting" (no comma will be provided only symbol will be there)
    
    Returns:
    - str: The formatted currency string.
    
    Raises:
    - TypeError: If unexpected keyword arguments are provided.
    
    Notes:
    - If no formatting options are provided, auto-formatting is determined based on the country or currency code.
    - Supports special numbering systems for India and China if the country code is 'IN', 'BD', 'NP', 'PK', or 'CN' respectively.
    """
    allowed_kwargs = ['place_currency_symbol_at_end', 'decimal_places', 'number_format_system']
    __unexpected_args_provided = []
    for kwarg in kwargs:
        if kwarg not in allowed_kwargs:
            __unexpected_args_provided.append(kwarg)
    if len(__unexpected_args_provided) > 0:
        raise TypeError(f"Unexpected keyword argument(s) '{__unexpected_args_provided}'\nAllowed kwargs are {allowed_kwargs}.")
    
    # Get the value(s) of kwargs
    place_currency_symbol_at_end = kwargs.get('place_currency_symbol_at_end', False)
    number_format_system = kwargs.get('number_format_system', 'auto').lower() #* to accept upper-case too

    autoformat = True
    indian_numbering_system = False
    china_numbering_system = False

    if currency_symbol or decimal_separator or thousands_separator:
        autoformat = False

    if autoformat:
        country = None
        currency_symbol = ''
        decimal_separator = '.'
        thousands_separator = ','
        decimal_places = kwargs.get('decimal_places', 2)

        if country_code:
            country = Country.load_country(country_code)
        if currency_code:
            country = Country.load_country_by_currency_code(currency_code)

        if country:
            if country.currency_symbol:
                currency_symbol = country.currency_symbol
            else:
                currency_symbol = country.currency_code

            country_code = country.alpha2
            currency_code = country.currency_code
            decimal_separator = country.currency_decimal_separator
            thousands_separator = country.currency_thousands_separator
            decimal_places = country.currency_decimal_place if "decimal_places" not in kwargs else decimal_places

    if country_code in ('IN', 'BD', 'NP', 'PK'):
        indian_numbering_system = True
 
    if country_code == 'CN':
        china_numbering_system = True
 
    if use_current_locale:
        localeconv = locale.localeconv()
        thousands_separator = localeconv.get('mon_thousands_sep', thousands_separator)
        decimal_separator = localeconv.get('mon_decimal_point', decimal_separator)

    formatting_precision = f'.0{decimal_places}f'
    formatting = '{:,' + formatting_precision + '}'

    # return formatting
    formatted_number = formatting.format(number)
    
    if number_format_system == 'international' or number_format_system == 'global':
        pass
    elif number_format_system == 'indian':
        formatted_number = format_india_numbering_system(formatted_number)
    elif number_format_system == 'chinese':
        formatted_number = format_china_numbering_system(formatted_number)
    elif number_format_system == 'auto':
        if indian_numbering_system:
            formatted_number = format_india_numbering_system(formatted_number)
        elif china_numbering_system:
            formatted_number = format_china_numbering_system(formatted_number)
    elif number_format_system == 'none':
        formatted_number = formatted_number.replace(',', '')
    else:
        raise ValueError(f"Invalid number_format_system '{number_format_system}'. Supported values are 'international', 'indian', 'chinese', 'auto', 'none'.")


    formatted_number = formatted_number.replace('.', '_')
    formatted_number = formatted_number.replace(',', thousands_separator)
    formatted_number = formatted_number.replace('_', decimal_separator)
    if place_currency_symbol_at_end:
        return f'{formatted_number} {currency_symbol}'.strip()
    return f'{currency_symbol} {formatted_number}'.strip()


def format_india_numbering_system(number_str):
    is_negative = number_str.startswith('-')

    if is_negative:
        number_str = number_str[1:]

    number_str = number_str.replace(',', '')
    s, *d = number_str.partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    result = "".join([r] + d)

    if is_negative:
        return '-' + result

    return result


def format_china_numbering_system(number_str):
    is_negative = number_str.startswith('-')

    if is_negative:
        number_str = number_str[1:]

    number_str = number_str.replace(',', '')
    s, *d = number_str.partition(".")
    r = ",".join([s[x-4:x] for x in range(-4, -len(s), -4)][::-1] + [s[-4:]])
    result = "".join([r] + d)

    if is_negative:
        return '-' + result

    return result
