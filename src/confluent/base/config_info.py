class ConfigInfo:
    def __init__(self, file_name: str, file_extension: str):
        self.file_name = file_name
        self.file_extension = file_extension.lstrip('.')
        self.file_name_full = f'{self.file_name}.{self.file_extension}'
