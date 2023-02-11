# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.


class ReportSection:
    def __init__(self, title, level):
        self.__title = title
        self.__level = level
        self.__contents = []

    @property
    def title(self):
        return self.__title

    @property
    def level(self):
        return self.__level

    @property
    def contents(self):
        return self.__contents

    def add_contents(self, *contents):
        for content in contents:
            self.__contents.append(content)
