import gspread
from gspread import Client, Spreadsheet, Worksheet
import pandas as pd


def get_all_values_in_ws(ws: Worksheet) -> list:
    list_of_lists = ws.get_all_values()
    return list_of_lists


class TableWorker:
    def __init__(
            self, url: str,
            id_gid_one_sm: list, id_gid_two_sm: list,
            id_gid_consult: list,
            id_gid_sub_lesson: list,
            path_service_account: str
    ):
        self._SPREADSHEET_UPL = url

        self._id_gid_one_sm = id_gid_one_sm
        self._id_gid_two_sm = id_gid_two_sm
        self._id_gid_consult = id_gid_consult
        self._id_gid_sub_lesson = id_gid_sub_lesson

        self._path_service_account = path_service_account
        self._gc: Client = gspread.service_account(self._path_service_account)
        self._sh: Spreadsheet = self._gc.open_by_url(self._SPREADSHEET_UPL)

        self.DataFrames = {}
        self.DataClasses = {}
        self.DataClasses_subLesson = {}

    def creatData(self):
        tmp_data = [get_all_values_in_ws(self._sh.get_worksheet_by_id(i)) for i in self._id_gid_one_sm]
        data_df = [pd.DataFrame(data=elem[1:], columns=elem[0]).rename(columns={
            'Дни': 'Дни' + str(i), 'Уроки': 'Уроки' + str(i), 'Время': 'Время' + str(i)
        }) for i, elem in enumerate(tmp_data)]
        result = pd.concat(data_df, axis=1)
        result = result[result.columns[:3].to_list() +
                        [i for i in result.iloc[:, 3:].columns if i not in result.columns[:3].to_list()]]
        result = result.rename(columns={i: i.lower().replace(' ', '').replace('+', '') for i in result.columns[3:]})
        result = result.rename(columns={'Дни0': 'Дни', 'Уроки0': 'Уроки', 'Время0': 'Время'})
        result['Дни'] = (result['Дни'].map(lambda x: x.lower()).replace('понедельник', 'ПН').replace('вторник', 'ВТ')
                         .replace('среда', 'СР').replace('четверг', 'ЧТ').replace('пятница', 'ПТ')
                         .replace('суббота', 'СБ'))
        self.DataFrames['gid_one'] = result

        tmp_data = [get_all_values_in_ws(self._sh.get_worksheet_by_id(i)) for i in self._id_gid_two_sm]
        data_df = [pd.DataFrame(data=elem[1:], columns=elem[0]).rename(columns={
            'Дни': 'Дни' + str(i), 'Уроки': 'Уроки' + str(i), 'Время': 'Время' + str(i)
        }) for i, elem in enumerate(tmp_data)]
        result = pd.concat(data_df, axis=1)
        result = result[result.columns[:3].to_list() +
                        [i for i in result.iloc[:, 3:].columns if i not in result.columns[:3].to_list()]]
        result = result.rename(columns={i: i.lower().replace(' ', '').replace('+', '') for i in result.columns[3:]})
        result = result.rename(columns={'Дни0': 'Дни', 'Уроки0': 'Уроки', 'Время0': 'Время'})
        result['Дни'] = (result['Дни'].map(lambda x: x.lower()).replace('понедельник', 'ПН').replace('вторник', 'ВТ')
                         .replace('среда', 'СР').replace('четверг', 'ЧТ').replace('пятница', 'ПТ')
                         .replace('суббота', 'СБ'))
        self.DataFrames['gid_two'] = result

        tmp_data = [get_all_values_in_ws(self._sh.get_worksheet_by_id(i)) for i in self._id_gid_sub_lesson]
        data_df = [pd.DataFrame(data=elem[1:], columns=elem[0]).rename(columns={
            'Дни': 'Дни' + str(i), 'Уроки': 'Уроки' + str(i), 'Время': 'Время' + str(i)
        }) for i, elem in enumerate(tmp_data)]
        result = pd.concat(data_df, axis=1)
        result = result[result.columns[:3].to_list() +
                        [i for i in result.iloc[:, 3:].columns if i not in result.columns[:3].to_list()]]
        result = result.rename(columns={i: i.lower().replace(' ', '').replace('+', '') for i in result.columns[3:]})
        result = result.rename(columns={'Дни0': 'Дни', 'Уроки0': 'Уроки', 'Время0': 'Время'})
        result['Дни'] = (result['Дни'].map(lambda x: x.lower()).replace('понедельник', 'ПН').replace('вторник', 'ВТ')
                         .replace('среда', 'СР').replace('четверг', 'ЧТ').replace('пятница', 'ПТ')
                         .replace('суббота', 'СБ'))
        self.DataFrames['gid_sub_lesson'] = result

        tmp_data = [get_all_values_in_ws(self._sh.get_worksheet_by_id(i)) for i in self._id_gid_consult]
        tmp_data = [pd.DataFrame(data=i[2:], columns=i[1]).rename(columns={'': 'Учителя'}) for i in tmp_data]
        data_consult = pd.concat(tmp_data, axis=0).reset_index().iloc[:, 1:]

        days_list = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
        k = 0
        for i in range(2, len(data_consult.columns), 2):
            data_consult[days_list[k]] = (
                    data_consult.iloc[:, i - 1] + ' ' + data_consult.iloc[:, i]
            )
            k += 1
        data_consult = data_consult.iloc[:, [0, 13, 14, 15, 16, 17, 18]]
        data_consult['Учителя'] = data_consult['Учителя'].map(lambda x: x.strip())
        self.DataFrames['gid_consult'] = data_consult

    def creatDataClasses(self):
        self.DataClasses = {str(i): [] for i in range(1, 12)}
        # print(self.DataFrames['gid'])
        for elem in list(self.DataFrames['gid_one'].columns)[3:]:
            chek_tmp = elem[:2]
            for symd in "йцукенгшщзхъфывапролджэячсмитьбю":
                chek_tmp = chek_tmp.replace(symd, '')
            for i in self.DataClasses:
                # print(chek_tmp, elem)
                if i == chek_tmp and all(['дни' not in elem, 'время' not in elem, 'уроки' not in elem]):
                    self.DataClasses[i].append(('/getTimeTable/' + elem + '/gid_one', elem))
        for elem in list(self.DataFrames['gid_two'].columns)[3:]:
            chek_tmp = elem[:2]
            for symd in "йцукенгшщзхъфывапролджэячсмитьбю":
                chek_tmp = chek_tmp.replace(symd, '')
            for i in self.DataClasses:
                # print(chek_tmp, elem)
                if i == chek_tmp and all(['дни' not in elem, 'время' not in elem, 'уроки' not in elem]):
                    self.DataClasses[i].append(('/getTimeTable/' + elem + '/gid_two', elem))

    def creatDataClasses_subLesson(self):
        self.DataClasses_subLesson = {str(i): [] for i in range(1, 12)}
        # print(self.DataFrames['gid_sub_lesson'])
        for elem in list(self.DataFrames['gid_sub_lesson'].columns)[3:]:
            chek_tmp = elem[:2]
            for symd in "йцукенгшщзхъфывапролджэячсмитьбю":
                chek_tmp = chek_tmp.replace(symd, '')
            for i in self.DataClasses_subLesson:
                # print(chek_tmp, elem)
                if i == chek_tmp and all(['дни' not in elem, 'время' not in elem, 'уроки' not in elem]):
                    self.DataClasses_subLesson[i].append(('/getTimeTable_subLesson/' + elem, elem))

    def get_Data(self, gid=False, gid_consult=False, gid_sub_lesson=False):
        if gid:
            return self.DataFrames
        if gid_consult:
            return self.DataFrames['gid_consult']
        if gid_sub_lesson:
            return self.DataFrames['gid_sub_lesson']
        return pd.DataFrame()

    def get_classes(self) -> dict:
        return self.DataClasses

    def get_classes_subLesson(self) -> dict:
        return self.DataClasses_subLesson

    def geter(self) -> dict:
        return {
            'SPREADSHEET_UPL': self._SPREADSHEET_UPL,
            'id_gid_one_sm': self._id_gid_one_sm,
            'id_gid_two_sm': self._id_gid_two_sm,
            'id_gid_sub_lesson': self._id_gid_sub_lesson,
            'id_gid_consult': self._id_gid_consult,
            'path_service_account': self._path_service_account,
            'Client': str(self._gc),
            'Spreadsheet': str(self._sh),
            'DataFrame': [self.DataFrames[i].values.tolist() for i in self.DataFrames],
            'DataClasses': self.DataClasses
        }