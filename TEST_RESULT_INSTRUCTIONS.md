# Инструкция по работе с результатами испытаний ГТО

## Обзор изменений

Добавлена модель `TestResult` для хранения результатов испытаний участников, которая позволяет:
- Хранить результаты по каждому упражнению для каждого участника
- Отслеживать полученные знаки отличия (золото, серебро, бронза)
- Вести историю сдачи нормативов по датам
- Автоматически заполнять федеральный шаблон реальными данными

## Модель TestResult

### Поля модели:
- `participant` - связь с участником (ForeignKey)
- `exercise` - связь с упражнением (ForeignKey)
- `result` - числовой результат (FloatField)
- `result_date` - дата сдачи испытания (DateField)
- `medal` - полученный знак отличия: gold/silver/bronze/none (CharField)
- `is_mandatory` - было ли испытание обязательным (BooleanField)
- `protocol_number` - номер протокола (CharField, опционально)
- `created_at` - дата создания записи (auto)
- `updated_at` - дата обновления записи (auto)

### Уникальность:
Комбинация `(participant, exercise, result_date)` должна быть уникальной.

## API Endpoints

### 1. Управление результатами испытаний

#### Получить все результаты:
```bash
GET /api/test-results/
Authorization: Token <your_token>
```

#### Фильтрация по участнику:
```bash
GET /api/test-results/?participant=<participant_id>
Authorization: Token <your_token>
```

#### Создать результат:
```bash
POST /api/test-results/
Authorization: Token <your_token>
Content-Type: application/json

{
    "participant": 1,
    "exercise": 5,
    "result": 12.5,
    "result_date": "2024-01-15",
    "medal": "gold",
    "is_mandatory": true,
    "protocol_number": "Протокол №123"
}
```

#### Обновить результат:
```bash
PATCH /api/test-results/<id>/
Authorization: Token <your_token>
Content-Type: application/json

{
    "result": 13.2,
    "medal": "gold"
}
```

#### Удалить результат:
```bash
DELETE /api/test-results/<id>/
Authorization: Token <your_token>
```

### 2. Экспорт в федеральный шаблон

```bash
POST /api/export-federal-template/
Authorization: Token <your_token>
Content-Type: application/json

{
    "participant_list_id": 1
}
```

**Ответ:** Excel-файл для скачивания с заполненными данными участников и их результатами.

## Примеры использования

### Пример 1: Добавление результата испытания через API

```javascript
// Frontend (JavaScript/React)
const addTestResult = async (participantId, exerciseId, result, medal) => {
    const response = await fetch('/api/test-results/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
        },
        body: JSON.stringify({
            participant: participantId,
            exercise: exerciseId,
            result: result,
            result_date: new Date().toISOString().split('T')[0],
            medal: medal,
            is_mandatory: true
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log('Результат добавлен:', data);
    }
};

// Пример: добавить результат бега на 100м
addTestResult(1, 5, 12.5, 'gold');
```

### Пример 2: Получение всех результатов участника

```javascript
const getParticipantResults = async (participantId) => {
    const response = await fetch(`/api/test-results/?participant=${participantId}`, {
        headers: {
            'Authorization': `Token ${token}`
        }
    });
    
    if (response.ok) {
        const results = await response.json();
        return results;
    }
};
```

### Пример 3: Экспорт федерального шаблона

```javascript
const exportFederalTemplate = async (participantListId) => {
    const response = await fetch('/api/export-federal-template/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
        },
        body: JSON.stringify({
            participant_list_id: participantListId
        })
    });
    
    if (response.ok) {
        // Скачивание файла
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `federal_template_${participantListId}.xlsx`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
};
```

### Пример 4: Массовое добавление результатов (Python/Django)

```python
from api.models import Participant, Exercise, TestResult
from datetime import date

# Получить участника
participant = Participant.objects.get(id=1)

# Получить упражнения для ступени
exercises = Exercise.objects.all()[:5]  # Первые 5 упражнений

# Добавить результаты
results_data = [
    {'exercise_id': 1, 'result': 12.5, 'medal': 'gold'},
    {'exercise_id': 2, 'result': 45, 'medal': 'silver'},
    {'exercise_id': 3, 'result': 180, 'medal': 'bronze'},
]

for data in results_data:
    exercise = Exercise.objects.get(id=data['exercise_id'])
    TestResult.objects.create(
        participant=participant,
        exercise=exercise,
        result=data['result'],
        result_date=date.today(),
        medal=data['medal'],
        is_mandatory=True,
        protocol_number="Протокол №123"
    )
```

## Интеграция с фронтендом

### Кнопка экспорта на React

```jsx
import React from 'react';

const ExportButton = ({ participantListId }) => {
    const handleExport = async () => {
        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch('/api/export-federal-template/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`
                },
                body: JSON.stringify({
                    participant_list_id: participantListId
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `federal_template_${participantListId}_${new Date().toISOString().split('T')[0]}.xlsx`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                const error = await response.json();
                alert(`Ошибка экспорта: ${error.error}`);
            }
        } catch (err) {
            console.error('Ошибка при экспорте:', err);
            alert('Произошла ошибка при экспорте файла');
        }
    };
    
    return (
        <button onClick={handleExport} className="btn btn-primary">
            📥 Экспорт в федеральный шаблон
        </button>
    );
};

export default ExportButton;
```

### Форма добавления результата

```jsx
import React, { useState } from 'react';

const AddTestResultForm = ({ participantId, onSuccess }) => {
    const [formData, setFormData] = useState({
        exercise: '',
        result: '',
        result_date: new Date().toISOString().split('T')[0],
        medal: 'none',
        is_mandatory: true
    });
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const token = localStorage.getItem('authToken');
        const response = await fetch('/api/test-results/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
            },
            body: JSON.stringify({
                participant: participantId,
                ...formData
            })
        });
        
        if (response.ok) {
            alert('Результат успешно добавлен!');
            setFormData({
                exercise: '',
                result: '',
                result_date: new Date().toISOString().split('T')[0],
                medal: 'none',
                is_mandatory: true
            });
            if (onSuccess) onSuccess();
        } else {
            const error = await response.json();
            alert(`Ошибка: ${JSON.stringify(error)}`);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <select 
                value={formData.exercise} 
                onChange={(e) => setFormData({...formData, exercise: e.target.value})}
                required
            >
                <option value="">Выберите упражнение</option>
                {/* Заполнить упражнениями из API */}
                <option value="1">Бег 30м</option>
                <option value="2">Бег 60м</option>
                <option value="3">Прыжок в длину</option>
            </select>
            
            <input
                type="number"
                step="0.01"
                placeholder="Результат"
                value={formData.result}
                onChange={(e) => setFormData({...formData, result: e.target.value})}
                required
            />
            
            <input
                type="date"
                value={formData.result_date}
                onChange={(e) => setFormData({...formData, result_date: e.target.value})}
                required
            />
            
            <select 
                value={formData.medal} 
                onChange={(e) => setFormData({...formData, medal: e.target.value})}
            >
                <option value="none">Без знака</option>
                <option value="bronze">Бронза</option>
                <option value="silver">Серебро</option>
                <option value="gold">Золото</option>
            </select>
            
            <label>
                <input
                    type="checkbox"
                    checked={formData.is_mandatory}
                    onChange={(e) => setFormData({...formData, is_mandatory: e.target.checked})}
                />
                Обязательное испытание
            </label>
            
            <button type="submit">Добавить результат</button>
        </form>
    );
};

export default AddTestResultForm;
```

## Административная панель Django

Модель `TestResult` зарегистрирована в админке Django. Для доступа:

1. Перейдите на `/admin/`
2. Авторизуйтесь как суперпользователь
3. Найдите раздел "Результаты испытаний"
4. Добавляйте, редактируйте или удаляйте результаты

## Проверка работы

### 1. Создание тестовых данных

```bash
cd /workspace
/workspace/venv/bin/python manage.py shell
```

```python
from api.models import Participant, Exercise, TestResult
from datetime import date

# Получить первого участника
participant = Participant.objects.first()
print(f"Участник: {participant}")

# Получить первое упражнение
exercise = Exercise.objects.first()
print(f"Упражнение: {exercise}")

# Создать результат
result = TestResult.objects.create(
    participant=participant,
    exercise=exercise,
    result=10.5,
    result_date=date.today(),
    medal='gold',
    is_mandatory=True
)
print(f"Создан результат: {result}")

# Проверить результаты участника
results = participant.test_results.all()
print(f"Все результаты участника: {list(results)}")
```

### 2. Тестирование API

```bash
# Получить токен
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Использовать токен для добавления результата
curl -X POST http://localhost:8000/api/test-results/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "participant": 1,
    "exercise": 1,
    "result": 12.5,
    "result_date": "2024-01-15",
    "medal": "gold",
    "is_mandatory": true
  }'
```

### 3. Тестирование экспорта

```bash
curl -X POST http://localhost:8000/api/export-federal-template/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"participant_list_id": 1}' \
  --output federal_template.xlsx
```

## Важные замечания

1. **Уникальность записей**: Нельзя добавить два результата для одного участника по одному упражнению в одну дату.

2. **Аутентификация**: Все API endpoints требуют аутентификации по токену.

3. **Валидация данных**: API автоматически проверяет наличие связанных объектов (participant, exercise).

4. **Производительность**: При большом количестве результатов используйте фильтрацию по participant_id.

5. **История изменений**: Моделируйте историю сдачи нормативов, создавая новые записи с разными датами, а не обновляя старые.

## Структура БД

```
Participant (Участник)
├── id
├── first_name
├── last_name
├── birth_date
└── test_results (связь)
    └── TestResult (Результат испытания)
        ├── id
        ├── participant_id → Participant.id
        ├── exercise_id → Exercise.id
        ├── result
        ├── result_date
        ├── medal
        └── ...

Exercise (Упражнение)
├── id
├── name
└── test_results (связь)
    └── TestResult
```

## Следующие шаги

1. ✅ Модель TestResult создана и миграция применена
2. ✅ API endpoints для CRUD операций доступны
3. ✅ Экспорт в федеральный шаблон использует реальные данные
4. ⬜ Добавить массовую загрузку результатов из Excel/CSV
5. ⬜ Добавить автоматический расчет знака отличия по результату
6. ⬜ Добавить валидацию результата по нормативам ступени
7. ⬜ Добавить статистику и аналитику по результатам
