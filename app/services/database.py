import os
from typing import Optional, List
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class DatabaseService:
    """Сервис для работы с базой данных PostgreSQL"""
    
    @staticmethod
    def connect_to_database():
        """Подключение к базе данных PostgreSQL"""
        try:
            connection = psycopg2.connect(
                user=os.getenv("DB_USER", "stock_user_serv"),
                password=os.getenv("DB_PASSWORD", "9y0h90MRO7Ay"),
                host=os.getenv("DB_HOST", "pg14-uran-prod.e-magnum.kz"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "stock")
            )
            return connection
        except Exception as error:
            print(f"Ошибка при подключении к БД: {error}")
            return None

    @staticmethod
    def get_actual_worked_hours(connection, supplier_name: str, start_date, end_date):
        """Получение фактически отработанных часов из merchandiser_log"""
        try:
            cursor = connection.cursor()
            
            query = """
            SELECT 
                m.supplier,
                SUM(ml.exit_date - ml.enter_date) AS total_worked_time
            FROM merchandiser_log ml
            JOIN merchandiser m 
                ON ml.merchantid = m.merchant_id
               AND ml.iin = m.iin
            WHERE ml.enter_date::date BETWEEN %s AND %s
              AND m.supplier = %s
            GROUP BY m.supplier
            """
            
            cursor.execute(query, (start_date, end_date, supplier_name))
            result = cursor.fetchone()
            
            cursor.close()
            
            if result:
                return result[1]  # total_worked_time
            else:
                return None
                
        except Exception as e:
            print(f"Ошибка при получении отработанных часов: {e}")
            return None

    @staticmethod
    def get_available_suppliers(connection) -> List[str]:
        """Получение списка доступных поставщиков из таблицы merch_fix"""
        try:
            cursor = connection.cursor()
            
            query = """
            SELECT DISTINCT "Supplier"
            FROM public.merch_fix 
            WHERE "Supplier" IS NOT NULL
            ORDER BY "Supplier"
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            
            suppliers = [result[0] for result in results]
            return suppliers
            
        except Exception as e:
            print(f"Ошибка при получении списка поставщиков: {e}")
            return []

    @staticmethod
    def get_planned_fte(connection, supplier_name: str, start_date, end_date):
        """Получение планируемого FTE из таблицы merch_fix"""
        try:
            cursor = connection.cursor()
            
            fte_query = """
            SELECT 
                "FTE"
            FROM public.merch_fix 
            WHERE "Month_date" >= %s 
              AND "Month_date" <= %s
              AND "Supplier" = %s
            LIMIT 1
            """
            
            cursor.execute(fte_query, (start_date, end_date, supplier_name))
            result = cursor.fetchone()
            
            cursor.close()
            
            if result:
                return result[0]  # fte
            else:
                return None
                
        except Exception as e:
            print(f"Ошибка при получении FTE: {e}")
            return None

    @staticmethod
    def find_supplier_by_code_or_name(connection, user_input: str) -> Optional[str]:
        """Поиск поставщика по коду или названию"""
        try:
            cursor = connection.cursor()
            
            # Сначала пытаемся найти по коду (если введено число)
            if user_input.isdigit():
                code_query = """
                SELECT DISTINCT "Supplier"
                FROM public.merch_fix 
                WHERE "Supplier" LIKE %s
                LIMIT 1
                """
                cursor.execute(code_query, (f"%({user_input})%",))
                result = cursor.fetchone()
                
                if result:
                    cursor.close()
                    return result[0]
            
            # Если не найден по коду или введено не число, ищем по названию
            name_query = """
            SELECT DISTINCT "Supplier"
            FROM public.merch_fix 
            WHERE "Supplier" ILIKE %s
            LIMIT 1
            """
            cursor.execute(name_query, (f"%{user_input}%",))
            result = cursor.fetchone()
            
            cursor.close()
            
            if result:
                return result[0]
            else:
                return None
                
        except Exception as e:
            print(f"Ошибка при поиске поставщика: {e}")
            return None