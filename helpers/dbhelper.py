# Define utility functions
def remove_keys_starting_with_underscore(data):
    """
    Removes keys starting with an underscore from a dictionary.
    """
    return {k: v for k, v in data.items() if not k.startswith('_')}

def find_invalid_columns_in_table(table, data):
    """
    Verifies if the input data keys match the table's columns.
    """
    table_keys = remove_keys_starting_with_underscore(vars(table))
    return [key for key in data if key not in table_keys]
