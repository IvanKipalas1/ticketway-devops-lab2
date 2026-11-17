# TicketWay

TicketWay — навчальний DevOps-проєкт системи бронювання квитків на події та концерти.

## Мета проєкту

Метою є створення системи бронювання квитків із використанням Docker, Kubernetes, GitHub Actions та інструментів моніторингу.

## Основні можливості

- реєстрація та авторизація користувачів;
- перегляд доступних подій;
- вибір і бронювання місць;
- тестова оплата бронювання;
- формування електронного квитка з QR-кодом;
- захист від подвійного бронювання.

## Архітектура

Проєкт складається з таких компонентів:

- `frontend` — вебінтерфейс користувача;
- `backend` — API та бізнес-логіка на FastAPI;
- `worker` — виконання фонових завдань;
- `tests` — автоматизовані тести;
- `infra` — конфігурації Kubernetes;
- `monitoring` — налаштування Prometheus.

Для зберігання даних використовується PostgreSQL.

## Docker

Для контейнеризації компонентів використовується Docker. За допомогою Docker Compose запускаються Backend, Frontend, PostgreSQL, Prometheus і Grafana.

## Kubernetes

Для розгортання компонентів TicketWay у Kubernetes створено відповідні конфігурації. Backend, Frontend, PostgreSQL і Worker працюють в окремих Pod.

## CI/CD

Для автоматизації перевірок використовується GitHub Actions.

Налаштовано:

- автоматичне тестування;
- перевірку синтаксису JavaScript;
- збірку Docker-образів;
- Matrix Build;
- Reusable Workflow;
- Conditional Jobs;
- навчальний Production Pipeline.

## Моніторинг

Для моніторингу використовується Prometheus і Grafana.

Prometheus збирає метрики Backend, а Grafana відображає доступність API, кількість HTTP-запитів, час відповіді та помилки.

## Структура репозиторію

```text
ticketway-devops-lab2/
├── .github/
│   └── workflows/
├── backend/
├── frontend/
├── worker/
├── tests/
├── infra/
│   └── k8s/
├── monitoring/
├── Dockerfile
├── docker-compose.yml
├── index.js
├── index.test.js
├── package.json
├── package-lock.json
└── README.md
```