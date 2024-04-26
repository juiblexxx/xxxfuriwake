# coding: utf-8

# 簡単ファイル振り分け [xxxfuriwake.py]
# GUI flet版 → やっぱり戻してPySimpleGUI版
# ※！！物凄く危険な操作なので注意して実行してください！！

# フォルダフラット化
# 指定フォルダ配下のサブフォルダにあるファイルを全て指定フォルダに移動します。
# 同一ファイル名が存在した場合は上書きします。
# 絶対にシステムフォルダの上位（C:\やC:\Windows等）で実行しない事！！

# 指定サイズ「以上」ファイル抽出
# 指定フォルダ以下から指定サイズ「以上」のファイルを出力先フォルダに集めます。
# サブフォルダ以下からも全て持ってきます。
# 絶対にシステムフォルダの上位（C:\やC:\Windows等）で実行しない事！！

# タイムスタンプ別振り分け
# 指定フォルダ以下のファイルをタイムスタンプのフォルダを掘ってそこにまとめます
# サブフォルダ以下から持ってきません

import os
import shutil
import copy
import datetime
# import re
# from typing import Tuple,List

import PySimpleGUI as sg
from tkinter import messagebox


def execute_files_to_flat(source_directory: str):
    # Tab1の処理
    kensu = 0

    # source_directoryのチェック
    if os.path.isdir(source_directory) :
        pass
    else:
        messagebox.showinfo("ディレクトリがありません", source_directory)
        return False

    # サブディレクトリ名のリストを取得
    file_list, subdirectory_list = get_list_file_and_directory(source_directory)

    # サブディレクトリ配下のファイルをsource_directoryにフラット化する
    kensu = move_files_recursive(source_directory, subdirectory_list)
    messagebox.showinfo("完了", str(kensu) + "件の移動がありました\n")


def execute_filesize_moving(source_directory: str, target_filesize_mb: int, output_directory: str):
    # Tab2の処理
    kensu = 0

    # source_directoryのチェック
    if os.path.isdir(source_directory) :
        pass
    else:
        messagebox.showinfo("ディレクトリがありません", source_directory)
        return False

    # 対象サイズを取得して100万倍する（指定はMbなので）
    target_filesize_byte = int(target_filesize_mb) * 1000 * 1000

    # output_directoryを作成する
    os.makedirs(output_directory, exist_ok=True)

    # ファイルリストとディレクトリリストを取得
    file_list, subdirectory_list = get_list_file_and_directory(source_directory)

    # 入力ディレクトリ直下にあるファイルを、サイズを指定してリストアップする
    targe_filesize_files = [f for f in file_list if os.path.isfile(os.path.join(source_directory, f)) and os.path.getsize(os.path.join(source_directory, f)) >= target_filesize_byte]

    # 配下のファイル群をoutput_directoryに移動する
    kensu += check_filename_before_moving(source_directory, output_directory, targe_filesize_files)

    # サブディレクトリ配下のファイルをoutput_directoryに移動する
    kensu += move_filesize_recursive(output_directory, subdirectory_list, target_filesize_byte)
    messagebox.showinfo("完了", str(kensu) + "件の移動がありました\n")


def execute_filedate_moving(source_directory: str, directory_suffix: str, date_flag: str):
    # Tab3の処理
    # directory_suffix = ディレクトリ名の接尾語
    # date_flag: "day" or "month"
    kensu = 0

    # source_directoryのチェック
    if os.path.isdir(source_directory) :
        pass
    else:
        messagebox.showinfo("ディレクトリがありません", source_directory)
        return False

    file_list, subdirectory_list = get_list_file_and_directory(source_directory)
    kensu = check_filedate_before_moving(source_directory, file_list, directory_suffix, date_flag)
    messagebox.showinfo("完了", str(kensu) + "件の移動がありました\n")


def get_list_file_and_directory(source_directory: str) -> tuple:
    """
    対象ディレクトリ直下のファイルとディレクトリを
    それぞれリスト化して返す
    Args:
        source_directory: 対象ディレクトリ
    Returns:
        file_list: 見つかったファイル名のリスト
        directory_list: 見つかったディレクトリのフルパスのリスト
    """
    names_all = os.listdir(source_directory)
    # names_allからファイル名のリストを作成
    file_list = [f for f in names_all if os.path.isfile(os.path.join(source_directory, f))]
    # names_allからディレクトリパスのリストを作成
    # source_directoryとjoinしておく
    directory_list = [os.path.join(source_directory, f) for f in names_all if os.path.isdir(os.path.join(source_directory, f))]
    # どっちも戻す
    return file_list, directory_list


def get_unique_filename(source_directory: str, source_filename: str) -> str:
    """
    source_directory+source_filenameが存在するかチェックし、
    存在していたらsource_filenameのファイル名部にアンダーバーを増やす
    存在が確認できなくなるまでアンダーバーを増やし、
    出来上がったファイル名を返す
    Args:
        source_directory: ファイルがあるディレクトリ
        source_filename: ファイル名
    Returns:
        そのディレクトリで重複のないファイル名
    """
    output_filename = copy.copy(source_filename)
    # 同一ファイル名があったら、同一でなくなるまでファイル名末尾にアンダーバーをつける
    while os.path.exists(os.path.join(source_directory, output_filename)) :
        # 引数をルートパスと拡張子に分けてくれる関数でファイル名を取得
        ftitle, fext = os.path.splitext(output_filename)
        # アンダーバー付けたoutput_filenameで再度評価
        output_filename = ftitle + "_" + fext
    return output_filename


def get_file_timestamp(file: str, format: int) -> str:
    """
    Args:
        file: ファイルのフルパス文字列
        format: 0 YYYY/mm/dd HH:MM:SS
                1 YYYYmmdd
                2 YYYY-MM-DD
                3 YYYY-MM
    Returns:
        ファイルから取得できたタイムスタンプ
    """
    try:
        t = os.path.getmtime(file)
        dt = datetime.datetime.fromtimestamp(t)
        if format == 0:
            ft = dt.strftime("%Y/%m/%d %H:%M:%S")
        elif format == 1:
            ft = dt.strftime("%Y%m%d")
        elif format == 2:
            ft = dt.strftime("%Y-%m-%d")
        elif format == 3:
            ft = dt.strftime("%Y-%m")
    except:
        ft = f"0000/00/00 00:00:00"
    return (ft)


def move_files_recursive(output_directory: str, directory_list: str) -> int:
    # 引数で渡されたディレクトリ一覧(directory_list)から一つ取り出し、
    # ファイル一覧とサブディレクトリ一覧を取得する。
    # ファイルならカレントに移動する（フラット化）
    # ディレクトリなら本メソッドを再起呼び出しする
    # [!!]C:\ とかで実行するとシステムが壊れるので何とかしなきゃ
    kensu = 0
    # files = []
    for source_directory in directory_list :
        file_list, subdirectory_list = get_list_file_and_directory(source_directory)
        # file_listがファイルならoutput_directoryに移動する
        kensu += check_filename_before_moving(source_directory, output_directory, file_list)
        # サブディレクトリ処理を実行（再起呼び出し）
        kensu += move_files_recursive(output_directory, subdirectory_list)
    return kensu


def check_filename_before_moving(source_directory: str, output_directory: str, file_list: str) -> int:
    # 渡されたファイルリスト(file_list)をsource_directoryからoutput_directoryに移動する
    # source_directoryのファイルがoutput_directoryに存在したらリネームする
    kensu = 0

    # source_directoryとoutput_directoryが同じだったら本処理は不要なのですぐ処理抜ける
    if (source_directory == output_directory):
        messagebox.showinfo("元と先のディレクトリが同じです。", source_directory)
        return kensu

    for source_filename in file_list :
        # 移動先のファイル名を取得（重複があったらファイル名はアンダーバーを増やす）
        output_filename = get_unique_filename(output_directory, source_filename)
        # アンダーバーのない名前
        source_path = os.path.join(source_directory, source_filename)
        # アンダーバーのあるかもしれない名前
        output_path = os.path.join(output_directory, output_filename)
        # 移動
        shutil.move(source_path, output_path)
        kensu += 1

    return kensu


def move_filesize_recursive(output_directory: str, directory_list: str, target_filesize: int) -> int:
    # directory_listをループで読み出し、ファイルかつtarget_filesize以上ならoutput_directoryに移動する
    kensu = 0
    files = []
    for df in directory_list :
        # dfがチェック対象ディレクトリ＝今回のカレント
        files = os.listdir(df)
        files_file = [f for f in files if os.path.isfile(os.path.join(df, f)) and os.path.getsize(os.path.join(df, f)) >= target_filesize]  # サイズを指定してファイルを取得
        kensu += check_filename_before_moving(df, output_directory, files_file)   # df配下のファイル群をoutput_directoryに移動する
        # print("%s %s %s" % (df, output_directory, files_file))

        file_directory = [os.path.join(df, f) for f in files if os.path.isdir(os.path.join(df, f))]
        # サブディレクトリ処理を実行（再起呼び出し）
        kensu += move_filesize_recursive(output_directory, file_directory, target_filesize)

    return kensu


def check_filedate_before_moving(source_directory: str, file_list: str, directory_suffix: str, date_type: str) -> int:
    # file_listをループで読み出し、source_directory配下に更新日ディレクトリを作成した後、そこに移動する
    # 既に同一ファイルが存在していたら、重複しなくなるまでファイル名にアンダーバーを増やしていく
    # directory_suffix: 作成ディレクトリ名の接尾語
    # date_type = "day" なら出力先は"YYYY-MM-DD"
    # date_type = "month" なら出力先は"YYYY-MM"
    kensu = 0

    for source_filename in file_list :
        # ソースディレクトリ＋ファイルのタイムスタンプで先にディレクトリを作成しておく
        # フォーマット2は「YYYY-MM-DD」形式
        # フォーマット3は「YYYY-MM」形式
        date_flag = 2
        if date_type == "day":
            date_flag = 2
        elif date_type == "month":
            date_flag = 3
        output_date = get_file_timestamp(os.path.join(source_directory, source_filename), date_flag)
        output_directory = os.path.join(source_directory, output_date + directory_suffix)
        os.makedirs(output_directory, exist_ok=True)

        # 移動先のファイル名を取得（重複があったらファイル名はアンダーバーを増やす）
        output_filename = get_unique_filename(output_directory, source_filename)

        # アンダーバーのない名前
        source_path = os.path.join(source_directory, source_filename)
        # アンダーバーのあるかもしれない名前
        output_path = os.path.join(output_directory, output_filename)
        # 移動
        shutil.move(source_path, output_path)
        kensu += 1

    return kensu


def check_system_path(source_path: str) -> bool:
    """
    Windowsのシステム系のパスが指定されたらFalseを返す
    引数の末尾の\\は削除（正規化）してからチェックする
    引数は全て小文字にしてからチェックする

    Args:
    path チェック対象のパス

    Returns:
    システム系のパスならFalse、システム系じゃなければTrue
    """
    check_result = True
    system_paths = ["c:", "c:\\", "c:\\windows", "c:\\user", "c:\\program files", "c:\\program files (x86)"]
    check_path = os.path.normpath(source_path)  # パスを正規化

    # 小文字にしてチェック
    if os.name == "nt" and check_path.lower() in system_paths:
        check_result = False

    return check_result

# カレントディレクトリを取得
current_path = os.path.dirname(__file__)

# layout定義-------------------------------------------------------------------------------------------------------------------
# sg.theme("Default")

TAB1_BUTTON_EXECUTE = "-TAB1_BUTTON_EXECUTE-"
TAB1_TEXT_DIRECTORY = "-TAB1_TEXT_DIRECTORY-"

tab1_layout = [
    [sg.Text("ソースディレクトリ配下にあるファイルを\n"
             "全てソースディレクトリに移し「フラット」にします。\n"
             "サブフォルダ配下のファイルも全て移ります。\n"
             "システムディレクトリを指定すると死にます。")],
    [sg.Text("ソース:"), sg.Input(current_path, key=TAB1_TEXT_DIRECTORY)],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Button("実行", key=TAB1_BUTTON_EXECUTE, size=(20,2))],
]

TAB2_BUTTON_EXECUTE = "-TAB2_BUTTON_EXECUTE-"
TAB2_TEXT_SOURCE_DIRECTORY = "-TAB2_TEXT_SOURCE_DIRECTORY-"
TAB2_TEXT_FILESIZE = "-TAB2_TEXT_FILESIZE-"
TAB2_TEXT_OUTPUT_DIRECTORY = "-TAB2_TEXT_OUTPUT_DIRECTORY-"

tab2_layout = [
    [sg.Text("ソースディレクトリ配下にあるファイルを、\n"
             "指定されたファイルサイズ(Mb)以上なら\n"
             "出力先ディレクトリに移します。\n"
             "システムディレクトリを指定すると死にます。")],
    [sg.Text("ソース:"), sg.Input(current_path, key=TAB2_TEXT_SOURCE_DIRECTORY)],
    [sg.Text("サイズ(Mb):"), sg.Input("500", key=TAB2_TEXT_FILESIZE)],
    [sg.Text("出力先:"), sg.Input(os.path.join(current_path, "big"), key=TAB2_TEXT_OUTPUT_DIRECTORY)],
    [sg.Button("実行", key=TAB2_BUTTON_EXECUTE, size=(20,2))],
]

TAB3_BUTTON_EXECUTE = "-TAB3_BUTTON_EXECUTE-"
TAB3_TEXT_SOURCE_DIRECTORY = "-TAB3_TEXT_SOURCE_DIRECTORY-"
TAB3_TEXT_SUFFIX = "-TAB3_TEXT_SUFFIX-"
TAB3_CHECKBOX_DAY = "-TAB3_CHECKBOX_DAY-"
TAB3_CHECKBOX_MONTH = "-TAB3_CHECKBOX_MONTH-"
TAB3_CHECKBOX_GID01 = "-TAB3_CHECKBOX_GID01-"

tab3_layout = [
    [sg.Text("ソースディレクトリ配下にあるファイルを、\n"
             "更新日時に基づいたフォルダを作成して振り分けます。\n"
             "チェックボックスの選択次第で日単位、月単位を選択可能。\n"
             "出力先フォルダ名の接尾語を追加できます。接尾語「_結婚式」→YYYY-MM-DD_結婚式\n"
             "サブディレクトリは見ないので、システムディレクトリを指定しても死にません。")],
    [sg.Radio("YYYY-MM-DD", key=TAB3_CHECKBOX_DAY, group_id=TAB3_CHECKBOX_GID01), sg.Radio("YYYY-MM", key=TAB3_CHECKBOX_MONTH, group_id=TAB3_CHECKBOX_GID01, default=True)],
    [sg.Text("接尾語:"), sg.Input("", key=TAB3_TEXT_SUFFIX)],
    [sg.Text("ソース:"), sg.Input(current_path, key=TAB3_TEXT_SOURCE_DIRECTORY)],
    [sg.Button("実行", key=TAB3_BUTTON_EXECUTE, size=(20,2))],
]

layout = [
    [sg.TabGroup([[
        sg.Tab("更新日振分", tab3_layout),
        sg.Tab("フラット化", tab1_layout),
        sg.Tab("サイズ超過抽出", tab2_layout),
    ]])],
]

# 表示ループ-------------------------------------------------------------------------------------------------------------------
window = sg.Window('xxxfuriwake', layout)

while True:
    event, values = window.read()
    print(event,values)
    if event == sg.WIN_CLOSED:
        break

    elif event == TAB1_BUTTON_EXECUTE:
        # フラット化処理
        if check_system_path(values[TAB1_TEXT_DIRECTORY]) == False:
            messagebox.showerror("中止", "システムフォルダでの実行はできません")
        else:
            if messagebox.askokcancel("確認", "実行してよろしいですか？"):
                execute_files_to_flat(values[TAB1_TEXT_DIRECTORY])

    elif event == TAB2_BUTTON_EXECUTE:
        # サイズ超過抽出処理
        if check_system_path(values[TAB2_TEXT_SOURCE_DIRECTORY]) == False:
            messagebox.showerror("中止", "システムフォルダでの実行はできません")
        else:
            if messagebox.askokcancel("確認", "実行してよろしいですか？"):
                execute_filesize_moving(values[TAB2_TEXT_SOURCE_DIRECTORY],values[TAB2_TEXT_FILESIZE],values[TAB2_TEXT_OUTPUT_DIRECTORY])

    elif event == TAB3_BUTTON_EXECUTE:
        # 更新日振り分け処理
        if check_system_path(values[TAB3_TEXT_SOURCE_DIRECTORY]) == False:
            messagebox.showerror("中止", "システムフォルダでの実行はできません")
        else:
            if messagebox.askokcancel("確認", "実行してよろしいですか？"):
                date_flag = "day"
                if values[TAB3_CHECKBOX_DAY]:
                    date_flag = "day"
                elif values[TAB3_CHECKBOX_MONTH]:
                    date_flag = "month"
                execute_filedate_moving(values[TAB3_TEXT_SOURCE_DIRECTORY], values[TAB3_TEXT_SUFFIX], date_flag)

window.close()
