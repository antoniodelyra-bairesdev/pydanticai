class EnvVariableMissingException(Exception):
    def __init__(self, env_variable_name: str):
        super().__init__(f'Variável de ambiente "{env_variable_name}" não definida.')
