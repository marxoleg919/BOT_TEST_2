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
    Принимает целое число от пользователя и выводит его факториал.
    """
    try:
        # Получаем ввод от пользователя
        number = int(input("Введите целое число: "))
        
        # Вычисляем факториал
        result = factorial(number)
        
        # Вычисляем факториал минус 1
        result_minus_one = factorial_minus_one(number)
        
        # Выводим результаты
        print(f"Факториал числа {number} равен {result}")
        print(f"Факториал числа {number} минус 1 равен {result_minus_one}")
        
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

