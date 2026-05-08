# Инструкция по экспорту в федеральный шаблон GTO

## Backend (Django)

### Созданный endpoint

**POST /api/export-federal-template/**

Этот endpoint принимает `participant_list_id` и возвращает Excel-файл в формате федерального шаблона GTO.

#### Аутентификация
Требуется токен аутентификации (TokenAuthentication).

#### Запрос
```http
POST /api/export-federal-template/
Authorization: Token <your-token>
Content-Type: application/json

{
    "participant_list_id": 1
}
```

#### Ответ
- **200 OK**: Возвращает Excel-файл для скачивания
- **400 Bad Request**: Если не указан `participant_list_id` или список пуст
- **404 Not Found**: Если список участников не найден

#### Заголовки ответа
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="federal_template_<name>_<date>.xlsx"
```

---

## Frontend (React/TypeScript пример)

### Пример компонента для выгрузки

```tsx
import React, { useState } from 'react';
import axios from 'axios';

interface ExportButtonProps {
  participantListId: number;
  participantListName: string;
}

export const ExportFederalTemplateButton: React.FC<ExportButtonProps> = ({
  participantListId,
  participantListName
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Получаем токен из хранилища (localStorage, sessionStorage, etc.)
      const token = localStorage.getItem('authToken');

      const response = await axios.post(
        '/api/export-federal-template/',
        { participant_list_id: participantListId },
        {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
          responseType: 'blob', // Важно: указываем что ожидаем бинарные данные
        }
      );

      // Создаем ссылку для скачивания файла
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Формируем имя файла из заголовка Content-Disposition
      const contentDisposition = response.headers['content-disposition'];
      let filename = `federal_template_${participantListName}_${new Date().toISOString().split('T')[0]}.xlsx`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch && filenameMatch[1]) {
          filename = decodeURIComponent(filenameMatch[1].replace(/utf-8''/gi, ''));
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Очищаем
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (err: any) {
      console.error('Ошибка экспорта:', err);
      if (err.response?.data) {
        // Читаем ошибку из ответа сервера
        const errorData = await err.response.data.text();
        try {
          const jsonError = JSON.parse(errorData);
          setError(jsonError.error || 'Ошибка экспорта');
        } catch {
          setError(errorData || 'Ошибка экспорта');
        }
      } else {
        setError('Ошибка соединения с сервером');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleExport}
        disabled={isLoading}
        style={{
          padding: '10px 20px',
          backgroundColor: isLoading ? '#ccc' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
        }}
      >
        {isLoading ? 'Экспорт...' : 'Выгрузить в федеральный шаблон'}
      </button>
      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          {error}
        </div>
      )}
    </div>
  );
};
```

### Использование в списке участников

```tsx
import React from 'react';
import { ExportFederalTemplateButton } from './ExportFederalTemplateButton';

const ParticipantListPage = () => {
  const participantList = {
    id: 1,
    name: 'Моя группа',
    // ... другие поля
  };

  return (
    <div>
      <h1>{participantList.name}</h1>
      
      {/* Кнопка экспорта */}
      <ExportFederalTemplateButton
        participantListId={participantList.id}
        participantListName={participantList.name}
      />
      
      {/* Таблица участников */}
      {/* ... */}
    </div>
  );
};

export default ParticipantListPage;
```

---

## Пример на JavaScript (без TypeScript)

```javascript
import axios from 'axios';

async function exportToFederalTemplate(participantListId, participantListName) {
  const token = localStorage.getItem('authToken');
  
  try {
    const response = await axios.post(
      '/api/export-federal-template/',
      { participant_list_id: participantListId },
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        responseType: 'blob',
      }
    );

    // Скачивание файла
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `federal_template_${participantListName}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return { success: true };
  } catch (error) {
    console.error('Ошибка экспорта:', error);
    return { 
      success: false, 
      error: error.response?.data?.error || 'Ошибка экспорта' 
    };
  }
}
```

---

## Структура заполняемого Excel-файла

Backend автоматически заполняет следующие поля в шаблоне `federal_template.xlsx`:

### Шапка протокола (лист "Протокол")
- **D4**: Регион (сейчас hardcoded "Удмуртская Республика")
- **A6**: Заголовок с указанием ступени
- **F7**: Ступень (определяется по возрасту первого участника)
- **G7**: Пол (определяется по первому участнику)
- **D13-O15**: Дата выполнения (текущая дата)
- **D8**: Наименование центра тестирования (берется из названия списка участников)
- **D9**: Адрес центра тестирования (пока пусто)

### Данные участников (начиная со строки 13)
- **A**: № п/п (автоматическая нумерация)
- **B**: Ф.И.О. (last_name first_name middle_name)
- **C**: Спортивное звание (пока пусто)
- **D**: УИН участника
- **E-O**: Результаты испытаний (11 колонок, пока пустые - требуется модель результатов)

---

## Примечания

1. **Результаты испытаний**: В текущей реализации результаты испытаний не заполняются, так как в модели данных отсутствует модель для хранения результатов выполнения упражнений участниками. Необходимо создать соответствующую модель (например, `ParticipantResult` с полями `participant`, `exercise`, `result_value`, `achieved_level` и т.д.).

2. **Ступень и пол**: Сейчас определяются по первому участнику в списке. Для списков с разнородными участниками рекомендуется либо:
   - Фильтровать участников по ступени/полу перед экспортом
   - Передавать параметры ступени и пола в запросе
   - Создавать отдельные списки для каждой ступени/пола

3. **Регион**: Захардкожен как "Удмуртская Республика". Можно добавить в настройки или передавать в запросе.

4. **Адрес центра тестирования**: Можно добавить поле `address` в модель `ParticipantList`.
