 
from requests import get

# Изменить на свое
owner = "music-blog" # Логин профиля Яндекс.Музыки (у кого берем треки)
kinds = "2096" # Номер ID плейлиста

# Не изменять
light = "false"
url = "https://music.yandex.ru/handlers/playlist.jsx"
#url = "https://music.mts.ru/handlers/playlist.jsx"


def get_json(request_url):
    """
    Получает данные в виде JSON по ссылке
    Вернет None если статус не 200
    """
    json_data = None
    document = get(request_url)
    if document.status_code == 200:
        json_data = document.json()

    return json_data


def create_list(input_data):
    """
    Создает лист. Каждый элемет листа - словарь.
    Словарь содержит:
    список исоплнителей, название трека, версию трека

    Вернет лист. Если входные данные не подходят - None
    """
    if 'playlist' not in input_data:
        return None
    else:
        input_data = input_data['playlist']['tracks']

    tracks = list()
    for track in input_data:
        singers = list()
        for artist in track['artists']:
            singers.append(artist['name'])

        title = track['title']

        version = None
        if 'version' in dict.keys(track):
            version = track['version']

        item = {'singers': singers, 'title': title, 'version': version}
        tracks.append(item)
    return tracks


def create_file(tracks):
    """
    Создает файл с именем "логин, id плейлиста, число треков"
    Строка выглядит как:
    Все исполнители трека - Название трека (Версия трека)
    Под версией понимается:
    Radio Edit, remix и прочее 
    """
    file_name = f"{owner}, id={kinds}, len={len(tracks)}.txt"
    file = open(file_name, "w", encoding="utf-8")
    for line in tracks:
        str = ""
        for artist in line['singers']:
            str += f"{artist} "

        str += f"- {line['title']}"
        if line['version'] is not None:
            str += f" ({line['version']})"
        file.write(f"{str}\n")
    file.close()
    print(f"Создан файл под названием '{file_name}'\nНайдите его в левой части экрана.")

def main():
    """

    """
    global owner, kinds
    if owner == "":
      print("\nУ кого берем треки?")
      owner = input("Введите логин -> ")
      while True:
        kinds = input("Введите ID плейлиста -> ")
        if not kinds.isdigit():
          print("Введите число")
        else:
          kinds = int(kinds)
          break 
    request_url = f"{url}?owner={owner}&kinds={kinds}&light={light}"
    print("Выполнение...")
    data = get_json(request_url)
    if data is not None:
        tracks = create_list(data)
        if tracks is not None:
            print("\nКоличество треков:", len(tracks))
            create_file(tracks)
    else:
        print("\nОшибка. Проверьте введенные данные.")
    return print("Скрипт завершен")


# Скрипт начинает работу только тогда, когда его запускают явно
# т. е. не импортируют
if __name__ == '__main__':
    main()
