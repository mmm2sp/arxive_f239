#This file is part of Get pho.rs!

#Get pho.rs! is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#Get pho.rs! is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along with Foobar. If not, see <https://www.gnu.org/licenses/>.

import requests
import os
import argparse

def change_html(data, url_type):
    '''
    Убирает лишние пробелы и переносы строк
    Позволяет обрабатывать перечисления и таблицы данных
    '''
    if data == "":
        return data

    data = data.replace("\n", "")
    data = data.replace("\r", "")
    data = data.lstrip()#Убирает пробелы в начале строки
    data = data.rstrip()#Убирает пробелы в конце строки

    data = data.replace("<br />", "\n")
    data = data.replace("<br>", "\n")
    
    data = data.replace("<strong>", "\\textbf{")
    data = data.replace("</strong>", "}")
    data = data.replace("<em>", "\\textit{")
    data = data.replace("</em>", "}")

    #Распознование списков
    data = data.replace("<ul>", "\\begin{itemize} \n")
    data = data.replace("</ul>", "\\end{itemize}")

    data = data.replace("<ol>", "\\begin{itemize} \n")
    data = data.replace("</ol>", "\\end{itemize}")
    
    data = data.replace("<li>", "\\item ")
    data = data.replace("</li>", "\n")


        
    #Обработка таблиц: определение числа столбцов
    idx_0 = data.find('<figure class="table">')
    idx = data.find("<tbody>", idx_0)
    while idx_0 != -1:
        str_idx = data.find("<tr>", idx)
        str_last_idx = data.find("</tr>", str_idx) 
        col_num = data[str_idx:str_last_idx:].count("</td>")
        table_type = "|"+"c|"*col_num

        end_table_idx = data.find("</tbody></table></figure>", str_last_idx)

        #Версия для стандартных таблиц
        table_data=data[idx + len("<tbody>"):end_table_idx:]
        table_data = table_data.replace("<tr>", "")
        table_data = table_data.replace("</tr>", '\\\ \n \\hline \n')
        table_data = table_data.replace("</td><td>", " & ")
        table_data = table_data.replace("<td>", "")
        table_data = table_data.replace("</td>", "")        

        if (data.rfind("</p>", 0, idx_0) != -1) and (idx_0 - data.rfind("</p>", 0, idx_0)<10): #Если недавно закончился </p>, то надо и таблицу окружить <p></p>
            data = data[:idx_0:] + " <p> \\begin{tabular}{"+table_type+"} \\hline \n" + table_data + \
            "\\end{tabular} </p>" + data[end_table_idx+len("</tbody></table></figure>")::]
            
        else:
            data = data[:idx_0:] + "\\begin{tabular}{"+table_type+"} \\hline \n" + table_data + \
            "\\end{tabular}" + data[end_table_idx+len("</tbody></table></figure>")::]

        idx_0 = data.find('<figure class="table">')
        idx = data.find("<tbody>", idx_0)


    if url_type == "-m": #Если разбалловка
        #Обработка таблиц разбалловок
        idx = data.find("<tbody>")
        while idx != -1:
            end_table_idx = data.find("</tbody>", idx)
            table_data = data[idx + len("<tbody>"):end_table_idx:].replace('$$', '$')

            #Обработка жирного текста и выделения разных методов
            idx_0 = table_data.find('<span class="')
            idx_1 = table_data.find('">', idx_0)
            idx_2 = table_data.find('</span>', idx_0)
            while idx_0 != -1:
                table_data = table_data[:idx_0:] + "\\textbf{" + table_data[idx_1 + len('">'):idx_2:] + \
                       "}" + table_data[idx_2 + len('</span>'):]
                idx_0 = table_data.find('<span class="')
                idx_1 = table_data.find('">', idx_0)
                idx_2 = table_data.find('</span>', idx_0)
            
            data = data[:idx:] + " <p> \\noindent \\begin{tabular}{|p{0.9 \\textwidth}|c|} \\hline \n" + \
                   table_data + \
                   "\\end{tabular} </p>" + data[end_table_idx+len("</tbody>")::]
            idx = data.find("<tbody>")


#Версия для менее стандартных таблиц

    first_idx = data.find("</td>")
    second_idx = data.find("<td", first_idx, len(data))
    while (second_idx != -1) and (data[first_idx:second_idx:].count("<tr>") == 0):
        last_idx = data.find(">", second_idx)
        data = data.replace(data[first_idx:last_idx+1:], " & ")
        first_idx = data.find("</td>")
        second_idx = data.find("<td", first_idx, len(data))

    idx = data.find("<td")
    while idx != -1:
        last_idx = data.find(">", idx)
        data = data.replace(data[idx:last_idx+1:], "")
        idx = data.find("<td")
    data = data.replace("<tr>", "")
    data = data.replace("</tr>", '\\\ \n \\hline \n')
    data = data.replace("</td>", "")
   
    return data

def no_spaces(string):
    '''
    Убирает лишние пробелы и переносы строк
    Заменяет html команды на ТЕХовские
    '''
    if string == "":
        return string
    #string = string.replace("\n\n\n", "\n\n")
    string = string.replace("\r", "")
    string = string.lstrip()#Убирает пробелы в начале строки
    string = string.rstrip()#Убирает пробелы в конце строки
    string = string.replace("$$\n\n$$", "")
    
    string = string.replace("&gt;", ">")
    string = string.replace("&lt;", "<")
    string = string.replace("&mdash;", "-")
    string = string.replace("%", "\%")
    string = string.replace("&#x27;", "'")
    string = string.replace("π", "\pi ")
    string = string.replace("&times;", "$\\times$")
    string = string.replace("&laquo;", '"')
    string = string.replace("&raquo;", '"')
    string = string.replace("&quot;", '"')
    string = string.replace("&nbsp;", ' ')
    string = string.replace("$,$", ", \,")


    

    #Костыль про patch-clamp
    string = string.replace("_\max", "_{\max}")
    
    return string


def clear_data(data, command):
    '''Вырезает куски вида <a...> ... </a> и <i...> ... </i>'''
    first_idx = data.find('<' + command, 0) 
    while first_idx != -1:
        last_idx = data.find('</' + command + '>', first_idx)
        data = data[:first_idx:] + data[last_idx + len('</' + command + '>')::]
        first_idx = data.find('<' + command, 0)
    return data

def insert_picture(f, data):
    #Картинка
    first_idx = data.find('<img src="', 0)
    if first_idx == -1: return data
    last_idx = data.find('.jpeg', first_idx)
    pic_name = data[first_idx + len('<img src="'):last_idx:] + '.jpeg'
    
    first_idx = data.find('style=', last_idx) + len ('style=')
    last_idx = data.find('/>', first_idx)
    pic_params = data[first_idx:last_idx:]
    pic_params = no_spaces(pic_params)

    first_idx = data.find('<div class=', last_idx)#"kt-section__info"', last_idx)
    if first_idx != -1:
        first_idx = data.find('>', first_idx) + 1
        last_idx = data.find('</div>', first_idx)
        pic_sub = data[first_idx:last_idx:]
        if pic_sub.count('<div')>0:
            pic_sub = ''
        pic_sub = no_spaces(pic_sub)
    else:
        pic_sub = ''
    first_idx = data.find('<div class="col-md-8 latexinput" >', 0)
    if first_idx != -1:
        last_idx = data.find('</div>', first_idx)
        text = data[first_idx + len('<div class="col-md-8 latexinput" >'):last_idx:]
        text = no_spaces(text)
    else:
        text = ""
    f.write("\QPicture{" + pic_name + "}{" + pic_params + "}{" + pic_sub + "}{" + text + "}\n\n")
    return data[:data.find('<img src="', 0):] + data[data.find('/>', 0) + 2::]

def save_MScheme(f, data):
    first_idx = data.find('<td style="width:90%;">', 0)
    if first_idx != -1:
        last_idx = data.find('</td>', first_idx)
        text = data[first_idx + len('<td style="width:90%;">'):last_idx:]
        tmp_idx_0 = text.find('<span class="label', 0)
        if tmp_idx_0 >= 0:
            tmp_idx_1 = text.find('>', tmp_idx_0)
            tmp_idx_2 = text.find('</span>', tmp_idx_1)
            version = text[tmp_idx_1 + 1:tmp_idx_2:]
            text = text[:tmp_idx_0:] + text[tmp_idx_2 + len('</span>'):]
        else:
            version = ""    
       
        text = no_spaces(text)

        bf_first_idx = text.find('<span class="font-weight-boldest">') #Если текст жирный
        if bf_first_idx != -1:
            bf_last_idx = text.find('</span>', bf_first_idx)
            bold_text = text[bf_first_idx + len('<span class="font-weight-boldest">'):bf_last_idx:]
            bold_text = no_spaces(bold_text)
            text = "\\textbf{"+bold_text+"}"

        text = insert_picture(f, text)

        first_idx = data.find('<td style="width:10%; text-align: center;">', last_idx)
        last_idx = data.find('</td>', first_idx)
        cost = data[first_idx + len('<td style="width:10%; text-align: center;">'):last_idx:]
        cost = no_spaces(cost)

        if version == "":
            f.write("\MBlock{" + cost + "}{" + text + "}\n\n")
        else:
            f.write("\MMBlock{" + cost + "}{" + version +  "}{" + text + "}\n\n")


def save_QBlock(f, data):
    first_idx = data.find('<span class="label label-lg font-weight-normal label-rounded label-inline label-primary mr-2">', 0)
    if first_idx == -1: return
    
    name_first_idx = data.find('>', first_idx) + 1
    name_last_idx = data.find('</span>', name_first_idx)
    if name_last_idx == -1: return
    name_str = data[name_first_idx:name_last_idx:]
    name_str = clear_data(name_str, "i")
    
    cost_first_idx = name_str.find('<sup>&nbsp;', 0)
    if cost_first_idx != -1:
        cost_last_idx = name_str.find('</sup>', 0)
        cost_str = name_str[cost_first_idx + len('<sup>&nbsp;'):cost_last_idx:]
        name_str = name_str[:cost_first_idx:] + name_str[cost_last_idx + len('</sup>')::]
    else: cost_str = ""

    name_str = no_spaces(name_str)

    first_idx = data.find('</span>', first_idx)
    if first_idx == -1: return
    last_idx = -1
    last_idx_1 = data.find("<phors-answer", first_idx + len('</span>'))
    last_idx_2 = data.find("<p></p>", first_idx + len('</span>'))
    if (last_idx_1 != -1) and (last_idx_2 > last_idx_1 or last_idx_2 == -1):
        last_idx = last_idx_1
    else:
        last_idx = last_idx_2
    if last_idx == -1:
        block = data[first_idx + len('</span>')::]
    else:
        block = data[first_idx + len('</span>'):last_idx:]
    block = no_spaces(block)
    block = block.replace('<p>', "")
    block = block.replace('</p>', "")
    
    f.write("\QBlock{" + name_str + "}{" + cost_str + "}{" + block + "}\n\n")


def save(f, data):
    #Обработка вложенных <p></p>. Рекурсивно отбрасываем по одной паре
    #Позволяет обрабатывать вложенные последовательно-параллельные конструкции вида:
        #<p>
        #    <p> ... </p><p> ... </p>
        #</p>
    first_idx = data.find('<p>', 0)
    last_idx = data.find('</p>', first_idx)
    if first_idx != -1:
        res = data[first_idx + len('<p>'):last_idx:]
        num_of_p = res.count('<p>')
        i = 0
        while i < num_of_p: #Если перед <\p> есть лишиние <p>
            last_idx = data.find('</p>', last_idx + 1)
            res = data[first_idx + len('<p>'):last_idx:]
            num_of_p = res.count('<p>')
            i = i + 1            
        save(f, data[:first_idx:])    
        save(f, res) #Сохраняем кусочек внутренности
        save(f, data[last_idx + len('</p>')::])
        return

   
    #В дате не осталось <p>...</p>
    data = clear_data(data, 'a') #Удаление неинформативного куска
    
   
    if max(data.find('</'), data.find('/>'), data.find('<!'), data.find('">')) == -1: #Если в дате только текст
        data = no_spaces(data)
        if data == "": return
        f.write("\QText{" + data + "}")
        f.write("\n\n")
        
    else: #Обработка случаев, когда в дате не только текст
        first_idx = data.find('<span class="label label-lg font-weight-normal label-rounded label-inline label-primary mr-2">', 0)
        #Если в дате есть "блок". 
        if  first_idx != -1:
            save_QBlock(f, data)
##        else:
##            first_idx = data.find('<tr>')  #Если в дате есть html-таблица. То есть режим разбалловки.
##            if first_idx != -1:
##                last_idx = data.find('</tr>', first_idx)
##                save(f, data[:first_idx:])
##                save_MScheme(f, data[first_idx + len('<tr>'): last_idx:])
##                save(f, data[last_idx + len('</tr>')::])
            
        else:
            first_idx = data.find('<span>Ответ:') #Если в дате есть блок с ответом. 
            if first_idx != -1:
                last_idx = data.find('</span>', first_idx)
                answer_block = data[first_idx + len('<span>Ответ:'):last_idx:]
                answer_block = no_spaces(answer_block)
                answer_block = insert_picture(f, answer_block)

                save(f, data[:first_idx:])
                f.write("\ABlock{" + answer_block + "}\n\n")
                save(f, data[last_idx + len('</span>')::])
            else:
                first_idx = data.find('<span class="font-weight-boldest">') #Если в дате есть заголовок.
                if first_idx != -1:
                    last_idx = data.find('</span>', first_idx)
                    chapter = data[first_idx + len('<span class="font-weight-boldest">'):last_idx:]
                    chapter = no_spaces(chapter)
                    f.write("\Chapter{" + chapter + "}\n\n")
                else:
                    #Картинка
                    data = insert_picture(f, data)
                    first_idx = -1 #FixMe: обработка картинок с подписями / просто текстом
    return
                    
def decipher_s(f, html):
    first_idx = html.find('<div class="card-body card-body-phors">')#Блоки с условием на странице с решением
    old_idx = first_idx + len('<div class="card-body card-body-phors">')
    while first_idx != -1:
        last_idx = html.find('<p></p>', first_idx)
        if last_idx >= 0:
            data = html[first_idx + len('<div class="card-body card-body-phors">'):last_idx + len('<p></p>'):]
            save(f, html[old_idx:first_idx:])
            save_QBlock(f, data)

            old_idx = last_idx + len('<p></p>')
            first_idx = html.find('<div class="card-body card-body-phors">', old_idx)
        else:
            first_idx = -1
            #Сюда не должно дойти
            print("Error: file ended while scaning the end of Question Block. This block was not created")
    save(f, html[old_idx::])
                    
def decipher_t(f, html):
    first_idx = html.find('<p>')#Обычный текст
    last_idx = html.rfind('</p>')#Обычный текст
    save(f, html[first_idx:last_idx+len('</p>'):])
                
def compile_page(url, url_num, url_type, problem_source, tex, pdf):
    #Дешифровка типа части задачи
    if url_type == "-s":
        problem_type = "Решение"
    else:
        if url_type == "-m":
            problem_type = "Разбалловка"
        else:
            problem_type = "Условие задачи"
  
    r = requests.get(url) #url - ссылка
    html = r.text

    #Считывание названия задачи
    first_idx = html.find('<title>', 0)
    last_idx = html.find('</title>', first_idx)
    problem_name = html[first_idx + len('<title>'):last_idx:]
    problem_name = problem_name.replace("Pho.rs:", "")
    problem_name = no_spaces(problem_name)

    if problem_name.find("Metronic | Login Page v3", 0) >= 0:
        print(url_num + " This page is empty now")
        return
    problem_name = problem_name.replace("?", "")

    if problem_source == "":
        #Считывание источника задачи
        idx = html.find('<div class="d-flex justify-content-between">', 0)#Источник задачи
        if idx == -1:
            problem_source = "Τ"
        else:
            idx = html.find('</i>', idx)
            last_idx = html.find('</a>', idx)
            problem_source = html[idx + len('</i>'):last_idx]
            problem_source = no_spaces(problem_source)
        

    file_name = problem_source + " " + problem_name + url_type
    file_name = file_name.replace('"', "")
    #Скачивние картинок со страницы
    last_idx = 0
    first_idx = html.find("/p/img/", last_idx + 1)
    while first_idx >= 0:
        last_idx = html.find("/", first_idx + len("/p/img/"))
        num = html[first_idx + len("/p/img/"):last_idx:]

        #Сохранение картинок
        new_idx = html.find('"', last_idx + 1)
        tmp_type = html[last_idx:new_idx:]
        p = requests.get("https://pho.rs/p/img/"+num+tmp_type)
        try:
            os.mkdir(file_name + "_files")
        except:
            tmp = 0
            
        name_txt = file_name + "_files/ReadMe.txt"
        out = open(name_txt, "w")
        out.write("This file and folder were created automatically. There will be pictures that are usefull to create pdf. Do not remove it")
        out.close()
        name_img = file_name + "_files/" + num + ".jpeg"
        out = open(name_img, "wb")
        out.write(p.content)
        out.close()
        
        html = html[:first_idx:] + name_img + html[last_idx + len(tmp_type)::]
        first_idx = html.find("/p/img/", last_idx + 1)

    #Начало работы над тех-файлом
    f = open(file_name +'.tex', 'w', encoding='utf-8') 
    f.write("\n")
    f.write("\\input{Preambula.tex}\n\n" )
    f.write("\\newcommand\ProblemName{" + problem_name + "}\n\n")
    f.write("\\newcommand\Source{" + problem_source + "}\n\n")
    f.write("\\newcommand\Type{" + problem_type + "}\n\n")
    f.write("\\input{Settings.tex}\n\n" )


    html = change_html(html, url_type)
    
    if url_type == "":
        decipher_t(f, html) #Анализ html и запись преобразованной информации в ТЕХ-файл
    else:
        decipher_s(f, html) #Анализ html и запись преобразованной информации в ТЕХ-файл

    f.write("\end{document}")
    f.close()

    if tex:
        os.system('pdflatex "' + file_name + '.tex"')
        os.system('pdflatex "' + file_name + '.tex"')
        if pdf:
            os.system('"' + file_name + '.pdf"')
    return


def error():
    print("URL is incorrect")

#############################

parser = argparse.ArgumentParser(description = 'Программа генерирует .tex и .pdf файлы с условиями / решениями задачи с сайта pho.rs')
parser.add_argument('page', metavar='page_number', type=str,
                    help='целое число, обозначающее номер страницы на сайте pho.rs. Например, если Вы хотите получить условие с pho.rs/p/504, нужно ввести 504')
parser.add_argument('--type', default='t', choices=['t', 's', 'm', 'a'], help='часть задачи. Введите "t", чтобы собрать условие, "s" -- решение, "m" -- разбалловку и "a" -- все вышеперечисленное')
parser.add_argument('--name', default='', help='источник задачи. Будет указан в начале названия файла для удобной сортировки. Если не указать, источник задачи будет определен автоматически при считывании с сайта')
parser.add_argument ('-tex', action='store_const', const=True, help='Установите, если НЕ нужно компилировать tex-файл. Соответственно не будет создан pdf-файл')
parser.add_argument ('-pdf', action='store_const', const=True, help='Установите, если НЕ нужно открывать готовый pdf-файл. Можно не указывать, если указан флаг "-tex"')

args = parser.parse_args()

url_num = str(args.page)
url_type = args.type

if (not url_num.isdigit()) or not (url_type == 't' or url_type == 's' or url_type == 'm' or url_type == 'h' or url_type == 'a'):
    error()
else:
    url = 'https://pho.rs/p/'
    url = url + str(url_num)
    if url_type == "a":
        compile_page(url, url_num, "", problem_source = args.name, tex = not args.tex, pdf = not args.pdf)
        compile_page(url + '/s', url_num, "-s", problem_source = args.name, tex = not args.tex, pdf = not args.pdf)
        compile_page(url + '/m', url_num, "-m", problem_source = args.name, tex = not args.tex, pdf = not args.pdf)
        compile_page(url + '/h', url_num, "-h", problem_source = args.name, tex = not args.tex, pdf = not args.pdf)
    else:
        if url_type != "t":
              url = url + '/' + str(url_type)
              url_type = "-" + url_type
        else: url_type = ""
        compile_page(url, url_num, url_type, problem_source = args.name, tex = not args.tex, pdf = not args.pdf)
