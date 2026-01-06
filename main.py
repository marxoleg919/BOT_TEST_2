def factorial(n):
    """
    Вычисляет факториал числа n.
    Факториал n! = 1 * 2 * 3 * ... * n
    """
    if n < 0:
        raise ValueError("Факториал определен только для неотрицательных чисел")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def factorial_minus_one(n):
    """
    Вычисляет факториал числа n и вычитает из него 1.
    Возвращает n! - 1
    """
    fact = factorial(n)
    return fact - 1


def main():
    """
    Основная функция программы.
    Показывает меню и позволяет пользователю выбирать команды.
    """
    print("Программа для работы с факториалом числа")
    print("----------------------------------------")
    while True:
        print("\nВыберите команду:")
        print("1 - Вычислить факториал числа")
        print("2 - Вычислить факториал числа и вычесть 1")
        print("3 - Выйти из программы")

        command = input("Введите номер команды (1/2/3): ").strip()

        if command == "3":
            print("Выход из программы. До свидания!")
            break

        if command not in ("1", "2"):
            print("Неизвестная команда. Пожалуйста, введите 1, 2 или 3.")
            continue

        try:
            # Получаем ввод от пользователя
            number = int(input("Введите целое число: "))

            # Вычисляем факториал
            result = factorial(number)

            if command == "1":
                # Команда 1: просто факториал
                print(f"Факториал числа {number} равен {result}")
            elif command == "2":
                # Команда 2: факториал минус 1
                result_minus_one = factorial_minus_one(number)
                print(f"Факториал числа {number} равен {result}")
                print(f"Факториал числа {number} минус 1 равен {result_minus_one}")

        except ValueError as e:
            # Ошибка преобразования строки в число
            if "invalid literal" in str(e):
                print("Ошибка: Введите корректное целое число.")
            else:
                print(f"Ошибка: {e}")
        except KeyboardInterrupt:
            print("\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()

