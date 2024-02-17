# Утилиты
import openpyxl


async def save_matrix_to_excel(matrix: list[list]) -> bool:
    """Функция записи матрицы в файл excel"""
    workbook = openpyxl.Workbook()
    # список заглавных букв латинского алфавита
    alphabet = [chr(i) for i in range(65, 91)]
    # определим стили сторон ячеек
    thins = openpyxl.styles.Side(border_style="medium", color="000000")

    # делаем единственный лист активным
    worksheet = workbook.active
    # меняем название листа
    worksheet.title = 'Список товаров'
    worksheet = workbook['Список товаров']
    # Первая строка
    worksheet.append(['product_id', 'category', 'vendor', 'description', 'price'])

    # ширина столбцов листа excel
    worksheet.column_dimensions['A'].width = 25
    worksheet.column_dimensions['B'].width = 25
    worksheet.column_dimensions['C'].width = 25
    worksheet.column_dimensions['D'].width = 75
    worksheet.column_dimensions['E'].width = 25

    # Установить высоту первой строки
    worksheet.row_dimensions[1].height = 20
    last_col_number = worksheet.max_column

    # номер последней строки
    row_number = worksheet.max_row

    for col_number in range(last_col_number):
        # границы ячейки
        worksheet[f'{alphabet[col_number]}{row_number}'].border = openpyxl.styles.Border(top=thins, bottom=thins,
                                                                                         left=thins, right=thins)
        # горизонтальное и вертикальное выравнивания, перенос текста
        worksheet[f'{alphabet[col_number]}{row_number}'].alignment = openpyxl.styles.Alignment(horizontal='left',
                                                                                               vertical='top',
                                                                                               wrap_text=False)
        # шрифт
        worksheet[f'{alphabet[col_number]}{row_number}'].font = openpyxl.styles.Font(name='Arial', size=12)
        # заливка
        worksheet[f'{alphabet[col_number]}{row_number}'].fill = openpyxl.styles.PatternFill(fill_type='solid', fgColor='CD7F32')

    # построчное добавление списка в первую свободную строку рабочего листа excel
    for row in matrix:
        worksheet.append(row)
        # номер последней строки
        row_number = worksheet.max_row
        # Установить высоту строки
        worksheet.row_dimensions[row_number].height = 13
        for col_number in range(last_col_number):
            # границы ячейки
            worksheet[f'{alphabet[col_number]}{row_number}'].border = openpyxl.styles.Border(top=thins, bottom=thins, left=thins, right=thins)
            # горизонтальное и вертикальное выравнивания, перенос текста
            worksheet[f'{alphabet[col_number]}{row_number}'].alignment = openpyxl.styles.Alignment(horizontal='left', vertical='top', wrap_text=False)
            # шрифт
            worksheet[f'{alphabet[col_number]}{row_number}'].font = openpyxl.styles.Font(name='Arial', size=10)
            # заливка
            worksheet[f'D{row_number}'].fill = openpyxl.styles.PatternFill(fill_type='solid', fgColor='F0F0F0')

    # делаем имя файла excel
    filename = 'excel_files/products.xlsx'

    # запись книги в excel-файл
    workbook.save(filename)
    return True


if __name__ == '__main__':
    folder = 'excel_files'

    matrix = [['1', '2', '3', '4', '5'], ['6', '7', '8', '9', '10']]
    print(save_matrix_to_excel(matrix))

