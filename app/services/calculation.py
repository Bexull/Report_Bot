from datetime import date
import calendar
from typing import Dict, Any

from app.config.settings import HOURS_PER_FTE, COST_PER_FTE, MONTH_NAMES
from .database import DatabaseService


class CalculationService:
    """Сервис для выполнения расчетов часов и стоимости"""
    
    @staticmethod
    def convert_interval_to_hours(interval) -> float:
        """Конвертация PostgreSQL interval в часы"""
        if interval is None:
            return 0
        
        days = interval.days if hasattr(interval, 'days') else 0
        seconds = interval.seconds if hasattr(interval, 'seconds') else 0
        
        total_hours = (days * 24) + (seconds / 3600)
        return total_hours

    @staticmethod
    def calculate_hours_analysis(planned_fte: float, actual_hours: float) -> Dict[str, Any]:
        """Расчет анализа часов (недоработка или переработка)"""
        
        planned_hours = planned_fte * HOURS_PER_FTE
        hours_difference = planned_hours - actual_hours
        
        if hours_difference > 0:
            unworked_fte = hours_difference / HOURS_PER_FTE
            cost = unworked_fte * COST_PER_FTE
            return {
                'type': 'underwork',
                'hours_difference': hours_difference,
                'fte_difference': unworked_fte,
                'cost': cost,
                'planned_hours': planned_hours
            }
        elif hours_difference < 0:
            overtime_hours = abs(hours_difference)
            overtime_fte = overtime_hours / HOURS_PER_FTE
            overtime_cost = overtime_fte * COST_PER_FTE
            return {
                'type': 'overtime',
                'hours_difference': overtime_hours,
                'fte_difference': overtime_fte,
                'cost': overtime_cost,
                'planned_hours': planned_hours
            }
        else:
            return {
                'type': 'exact',
                'hours_difference': 0,
                'fte_difference': 0,
                'cost': 0,
                'planned_hours': planned_hours
            }

    @staticmethod
    async def perform_calculation(supplier_name: str, start_date: date, end_date: date) -> str:
        """Выполнение полного расчета часов"""
        connection = DatabaseService.connect_to_database()
        if connection is None:
            return "❌ Ошибка подключения к базе данных"
        
        try:
            # Получаем фактически отработанные часы
            actual_worked_time = DatabaseService.get_actual_worked_hours(
                connection, supplier_name, start_date, end_date
            )
            if actual_worked_time is None:
                return "❌ Не удалось получить данные об отработанных часах"
            
            actual_hours = CalculationService.convert_interval_to_hours(actual_worked_time)
            
            # Получаем планируемый FTE
            planned_fte = DatabaseService.get_planned_fte(
                connection, supplier_name, start_date, end_date
            )
            if planned_fte is None:
                return "❌ Не удалось получить данные о FTE"
            
            # Рассчитываем анализ
            analysis = CalculationService.calculate_hours_analysis(planned_fte, actual_hours)
            
            # Формируем результат
            return CalculationService.format_calculation_result(
                supplier_name, start_date, end_date, actual_hours, planned_fte, analysis
            )
            
        except Exception as e:
            print(f"Ошибка при расчете: {e}")
            return f"❌ Ошибка при расчете: {e}"
        finally:
            connection.close()

    @staticmethod
    def format_calculation_result(
        supplier_name: str, 
        start_date: date, 
        end_date: date, 
        actual_hours: float, 
        planned_fte: float, 
        analysis: Dict[str, Any]
    ) -> str:
        """Форматирование результата расчета"""
        
        result = f"""
📊 <b>Результат расчета</b>

🏢 <b>Поставщик:</b> {supplier_name}
📅 <b>Период:</b> {MONTH_NAMES[start_date.month-1].title()} {start_date.year}
📅 <b>Даты:</b> {start_date} - {end_date}

⏰ <b>Фактически отработано:</b> {actual_hours:.2f} часов
📈 <b>Фактически отработано FTE:</b> {actual_hours / HOURS_PER_FTE:.2f}
📊 <b>Планируемые часы:</b> {analysis['planned_hours']:.2f} часов
📈 <b>Планируемый FTE:</b> {planned_fte:.2f}

"""
        
        if analysis['type'] == 'underwork':
            result += f"""
❌ <b>НЕДОРАБОТКА</b>
⏰ Неотработано часов: {analysis['hours_difference']:.2f}
📉 Неотработано FTE: {analysis['fte_difference']:.2f}
💰 Стоимость неотработанных часов: {analysis['cost']:,.0f} тенге
"""
        elif analysis['type'] == 'overtime':
            result += f"""
🔄 <b>ПЕРЕРАБОТКА</b>
⏰ Переработано часов: {analysis['hours_difference']:.2f}
📈 Переработано FTE: {analysis['fte_difference']:.2f}
💰 Стоимость переработки: {analysis['cost']:,.0f} тенге
"""
        else:
            result += f"""
✅ <b>РАБОТА ВЫПОЛНЕНА ТОЧНО ПО ПЛАНУ!</b>
💰 Дополнительная стоимость: 0 тенге
"""
        
        return result