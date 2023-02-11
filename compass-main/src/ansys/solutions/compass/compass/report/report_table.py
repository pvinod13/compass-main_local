# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.


class ReportTable:
    def __init__(self, caption, content):
        self.__caption = caption
        self.__content = content

    @property
    def content(self):
        return self.__content

    @property
    def caption(self):
        return self.__caption
