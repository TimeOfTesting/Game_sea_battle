from random import randint
import time

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Point ({self.x},{self.y})'

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Ваш выстрел выходит за пределы доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту точку!"

class BoardWrongShipException(BoardException):
    pass


class Ship:

    def __init__(self, point, length, ship_direction):
        self.point = point
        self.length = length
        self.ship_direction = ship_direction
        self.count_lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.point.x
            cur_y = self.point.y
            if self.ship_direction == 0:
                cur_x += i
            elif self.ship_direction == 1:
                cur_y += i
            ship_dots.append(Point(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:

    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [[' '] * self.size for _ in range(self.size)]
        self.busy = []
        self.ships = []

    def out(self, point):
        return not ((0 <= point.x < self.size) and (0 <= point.y < self.size))

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = 'X'
            self.busy.append(d)
        self.ships.append(ship)
        self.counter(ship)

    def counter(self, ship, verb=True):
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)]
        for i in ship.dots:
            for dx, dy in near:
                cur = Point(i.x + dx, i.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def __str__(self):
        result = ''
        for i in range(1, self.size + 1):
            result += ' | ' + str(i)
        result += ' | '
        for index, row in enumerate(self.field):
            result += f'\n{index + 1}| ' + ' | '.join(row) + ' | '

        if self.hid:
            result = result.replace('X', 'X')
        return result

    def shot(self, point):
        if self.out(point):
            raise BoardOutException()

        if point in self.busy:
            raise BoardUsedException()
        self.busy.append(point)

        for ship in self.ships:
            if ship.shooten(point):
                ship.count_lives -= 1
                self.field[point.x][point.y] = '*'
                if ship.count_lives == 0:
                    self.count += 1
                    self.counter(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True
        self.field[point.x][point.y] = '*'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []

class Player:

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):

    def ask(self):
        point = Point(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {point.x + 1} {point.y + 1}")
        return point

class User(Player):

    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите две координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Point(x - 1, y - 1)

class Game:
    
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for i in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print('_' * 25)
        print("  Приветствуем Вас  ")
        print("      в игре       ")
        print("    'Морской бой'    ")
        print('_' * 25)
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")


    def print_boards(self):
        print("-" * 25)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 25)
        print("Доска компьютера:")
        print(self.ai.board)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-" * 25)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 25)
                print("Ходит компьютер!")
                time.sleep(3)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                self.print_boards()
                print("-" * 25)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                self.print_boards()
                print("-" * 25)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

game = Game()
game.start()










