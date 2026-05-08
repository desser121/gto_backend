# Множественные результаты испытаний

## 📋 Описание проблемы

Ранее участник мог иметь только **один результат** по каждому упражнению из-за ограничения `unique_together = ['participant', 'exercise', 'result_date']` в модели `TestResult`.

Это не позволяло:
- Участнику пересдавать нормативы
- Хранить историю попыток
- Выбирать лучший результат для экспорта

## ✅ Выполненные изменения

### 1. **Модель TestResult** (`api/models.py`)

**Удалено ограничение уникальности:**
```python
class Meta:
    # unique_together = ['participant', 'exercise', 'result_date']  # Закомментировано
    ordering = ['-result_date', 'participant']
```

**Теперь участник может:**
- Сдавать одно упражнение **неограниченное количество раз**
- Иметь разные результаты в разные даты
- Получать разные знаки отличия за каждую попытку

### 2. **Логика выбора лучшего результата** (`api/views.py`)

Обновлен метод `_get_participant_normatives()`:

```python
def _get_participant_normatives(self, participant, step_name, exercises):
    """
    Возвращает ЛУЧШИЙ результат по каждому упражнению.
    
    Учитывает тип упражнения:
    - is_higher_better=True (отжимания, прыжки) → выбирается МАКСИМАЛЬНЫЙ результат
    - is_higher_better=False (бег) → выбирается МИНИМАЛЬНЫЙ результат
    """
```

**Алгоритм:**
1. Группирует все результаты участника по упражнениям
2. Для каждого упражнения определяет тип (лучше больше или меньше)
3. Выбирает лучший результат согласно типу упражнения
4. Возвращает словарь лучших результатов для экспорта

### 3. **Миграция**

Создана миграция `0009_remove_testresult_unique_together.py`:
```bash
./venv/bin/python manage.py makemigrations api --name remove_testresult_unique_together
./venv/bin/python manage.py migrate
```

## 🧪 Тестирование

Созданы тестовые данные:
- Участник: Иванов Иван
- 3 упражнения с **двумя результатами** каждое (разные даты, разные медали)

**Результаты тестирования:**

| Упражнение | Результат 1 | Результат 2 | Лучший |
|------------|-------------|-------------|--------|
| Бег 10м (is_higher_better=False) | 10.5 (Золото) | 11.5 (Серебро) | **10.5** ✅ |
| Бег 30м (is_higher_better=False) | 11.5 (Золото) | 12.5 (Серебро) | **11.5** ✅ |
| Пресс (is_higher_better=True) | 12.5 (Золото) | 13.5 (Серебро) | **13.5** ✅ |

**Проверка через API:**
```python
from api.serializers import ParticipantSerializer
participant = Participant.objects.first()
serializer = ParticipantSerializer(participant)

# Возвращает ВСЕ 6 результатов (2 на каждое из 3 упражнений)
print(len(serializer.data['test_results']))  # 6
```

**Проверка экспорта:**
```python
from api.views import ExportFederalTemplateView
view = ExportFederalTemplateView()
norms = view._get_participant_normatives(participant, step_name, exercises)

# Возвращает только ЛУЧШИЕ результаты (по 1 на упражнение)
print(norms)  # {'Бег 10м': 10.5, 'Бег 30м': 11.5, 'Пресс': 13.5}
```

## 📊 Как это работает на практике

### Сценарий 1: Участник пересдает норматив

1. **Понедельник**: Бег 10м → 11.5 сек (Серебро)
2. **Среда**: Бег 10м → 10.5 сек (Золото) ← лучше
3. **Экспорт в Excel**: Автоматически подставится **10.5**

### Сценарий 2: Разные типы упражнений

**Для бега (чем меньше, тем лучше):**
- Попытка 1: 12.0 сек
- Попытка 2: 11.5 сек ← **будет использован в экспорте**
- Попытка 3: 12.5 сек

**Для пресса (чем больше, тем лучше):**
- Попытка 1: 45 раз
- Попытка 2: 52 раза ← **будет использован в экспорте**
- Попытка 3: 48 раз

## 🔗 API Endpoints

### Получить все результаты участника
```http
GET /api/test-results/?participant=<id>
```

Ответ содержит **ВСЕ** попытки:
```json
{
  "count": 6,
  "results": [
    {"exercise_name": "Бег 10м", "result": 10.5, "medal": "gold"},
    {"exercise_name": "Бег 10м", "result": 11.5, "medal": "silver"},
    ...
  ]
}
```

### Экспорт в федеральный шаблон
```http
POST /api/export-federal-template/
Content-Type: application/json

{"participant_list_id": 1}
```

В Excel файл будут записаны **только лучшие результаты** по каждому упражнению.

## 💡 Рекомендации для фронтенда

### Отображение истории попыток
```javascript
// Показать все попытки
axios.get(`/api/test-results/?participant=${participantId}`)
  .then(response => {
    // Группируем по упражнениям
    const grouped = {};
    response.data.results.forEach(result => {
      if (!grouped[result.exercise]) {
        grouped[result.exercise] = [];
      }
      grouped[result.exercise].push(result);
    });
    
    // Отображаем историю по каждому упражнению
    Object.entries(grouped).forEach(([exercise, attempts]) => {
      console.log(`${exercise}: ${attempts.length} попыток`);
      console.log(`Лучший: ${Math.min(...attempts.map(a => a.result))}`); // для бега
    });
  });
```

### Добавление новой попытки
```javascript
// Просто создаем новую запись - ограничений больше нет
axios.post('/api/test-results/', {
  participant: participantId,
  exercise: exerciseId,
  result: 10.5,
  result_date: '2026-05-08',
  medal: 'gold',
  is_mandatory: true
});
```

## ⚠️ Важные замечания

1. **Автоматический выбор лучшего** работает только при экспорте в Excel
2. **API возвращает все попытки** - фронтенд должен сам решать, какую показывать как основную
3. **is_higher_better** берется из модели `Normative` для соответствующей ступени
4. Если норматив не найден, по умолчанию используется `is_higher_better=False` (как для бега)

## 📝 Следующие шаги (опционально)

- [ ] Добавить поле `is_best` в модель `TestResult` для ручного标记 лучшего результата
- [ ] Создать endpoint для автоматического пересчета всех лучших результатов
- [ ] Добавить валидацию: не более N попыток за период
- [ ] Вести статистику прогресса участника по времени
