<img width="1200" height="800" alt="resort" src="https://github.com/user-attachments/assets/e6f24084-0363-4594-bb3f-b4fdc7cf8196" />


# 🏨 Resort Agentic AI Chatbot

A **stateful, multi-agent AI chatbot** for resort management, capable of handling **room bookings, food ordering, and room services** through natural language conversations.

This project demonstrates an **Agentic AI architecture** with intent routing, conversation memory, database-backed actions, and a Streamlit-based UI.

---

###

- Akshat Thapa
- Biomedical Engineering
- School of Medical Science & Technology
- Indian Institute of Technology Kharagpur (IITKGP)

## ✨ Features

### 🤖 Agentic Architecture

The system is composed of specialized agents:

- **Receptionist Agent**
  - Room booking  
  - Check-in / check-out  
  - Facility information  

- **Restaurant Agent**
  - Menu display (from database)  
  - Food ordering (one order per conversation)  
  - Order confirmation and database storage  

- **Room Service Agent**
  - Cleaning requests  
  - Laundry and amenities  
  - Request logging  

---

### 🧠 Intelligent Intent Routing

- User messages are routed using an **intent router**
- Once an agent is engaged, the **intent is locked** until the task completes
- Prevents mid-conversation misclassification (core agentic behavior)

---

### 💾 Persistent Memory

- Conversation context stored per `conversation_id`
- Tracks stages like:
  - `awaiting_item`
  - `awaiting_quantity`
  - `awaiting_room_number`
  - `awaiting_confirmation`
- Context is **cleared automatically** after task completion

---

### 🗄️ Database Integration

- MySQL backend using SQLAlchemy
- Stores:
  - Menu items
  - Orders & order items
  - Room availability
  - Room service requests

---

### 🖥️ Interactive UI

- Streamlit-based chat interface
- Dynamic menu selection
- Button-based confirmations for improved UX

---

## Tech Stack

| Layer | Technology |
|------|-----------|
| Backend | Flask |
| Frontend | Streamlit |
| LLM | OpenAI (via LangChain) |
| Database | MySQL |
| ORM | SQLAlchemy |
| Memory | In-memory conversation store |
| Architecture | Agentic AI (multi-agent routing) |

---

## 📂 Project Structure

```text
Resort-AgenticAI/
│
├── agents/
│   ├── router_agent.py
│   ├── receptionist_agent.py
│   ├── restaurant_agent.py
│   └── room_service_agent.py
│
├── models/
│   ├── room.py
│   ├── menu.py
│   ├── order.py
│   ├──service_request.py
|   ├──base.py 
│
├── routes/
│   └── menu.py
│
├── memory/
│   └── conversation_store.py
│
├── ui/
|    ├──admin_dashboard.py
|    ├──chat_ui.py
|
├── app.py
├── db.py
├── init_db.py
├── venv
├── .gitignore
├── requirements.txt
└── README.md
```
## 🛠️ Tool Calling / Function Calling Design

This project follows a **deterministic tool-calling approach** instead of relying on fully autonomous LLM function calls.  
Each agent explicitly invokes **backend tools (database operations, state updates)** based on the conversation stage.

---

### 🔧 “Tools” used in This Project

In this system, **tools = backend functions** that perform real actions such as:

- Fetching menu items from the database
- Creating food orders
- Booking rooms
- Logging room service requests
- Updating availability or status

These tools are **Python functions**

---

### 🧠 How Tool Calling Works

```text
User Message
   ↓
Router Agent (Intent Detection)
   ↓
Specific Agent (Restaurant / Reception / Room Service)
   ↓
Conversation State Check
   ↓
Tool Invocation (DB / Business Logic)
   ↓
Structured Response to User
```

##  How to Run the Project

1️⃣ Clone the Repository
2️⃣ Create Virtual Environment
```text
python -m venv venv
venv\Scripts\activate   # Windows
```
3️⃣ Install Dependencies
```text
pip install -r requirements.txt
```
4️⃣ Set Environment Variables
```text
Create a .env file in the project root:
OPENAI_API_KEY=your_openai_api_key
DB_USER=your_db_user
DB_PASSWORD=your_mysql_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name
```
5️⃣ Run Backend (Flask)
```text
python app.py
```

6️⃣ Run Frontend (Streamlit)
For user-agent chat
```text
streamlit run .\ui\chat_ui.py
```
For Dashboard:
```text
streamlit run .\ui\admin_dashboard.py
```
## Agentic Design Highlights

-Intent Locking – prevents agent switching mid-task

-Deterministic Flows – no hallucinations for transactional actions

-Clear Agent Boundaries – single responsibility per agent

-Extensible Design – easy to add billing, kitchen dashboard, admin tools in the future works

## Sample chat conversations between user and Restaurant_agent
```text
User: I want to order food
Bot: Shows menu
User: Butter Chicken
Bot: How many servings?
User: 1
Bot: Please provide room number
User: 101
Bot: Order summary
User: YES
Bot: ✅ Order confirmed!
```
## Sample chat conversations between user and Reception_agent
```text
User: book a room
Bot: The following rooms are available: ['102', '202'] Please tell me which room you'd like to book.
User: 102
Bot: ✅ Room 102 has been successfully booked for you!
```
## Sample chat conversations between user and Room_service_agent
```text
User: I need toilet paper
Bot: Sure. Please provide your room number so I can log the request.
User: 102
Bot: ✅ Your request has been logged successfully. Request type: General Room Service Room number: 102 Status: Pending
User: Thanks
Bot: You're welcome! If you have any other questions or need assistance, feel free to ask. Enjoy your day!
User: 102 room service completed
Bot: ✅ Your room service request for room 102 has been marked as COMPLETED. Thank you for confirming!
 
