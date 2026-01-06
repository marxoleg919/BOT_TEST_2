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


def main():
    """
    Основная функция программы.
    Принимает целое число от пользователя и выводит его факториал.
    """
    try:
        # Получаем ввод от пользователя
        number = int(input("Введите целое число: "))
        
        # Вычисляем факториал
        result = factorial(number)
        
        # Выводим результат
        print(f"Факториал числа {number} равен {result}")
        
    except ValueError as e:
        if "invalid literal" in str(e):
            print("Ошибка: Введите корректное целое число")
        else:
            print(f"Ошибка: {e}")
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()

