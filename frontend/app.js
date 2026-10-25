const conversation = document.getElementById("conversation");
const welcome = document.getElementById("welcome");
const messagesElement = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const chatList = document.getElementById("chat-list");

let nextId = 2;
let activeChatId = 1;

const chats = [{
    id: 1,
    title: "Новый диалог",
    messages: []
}];

function renderChatList() {
    chatList.replaceChildren();

    chats.forEach(chat => {
        const button = document.createElement("button");
        button.className = "chat-item" + (chat.id === activeChatId ? " active" : "");
        button.textContent = chat.title;
        button.title = chat.title;
        button.addEventListener("click", () => {
            activeChatId = chat.id;
            renderChatList();
            renderMessages();
        });
        chatList.appendChild(button);
    });
}

function addMessage(role, text) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = role === "user" ? "Вы" : "Демонстрационный помощник";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    wrapper.append(label, bubble);
    messagesElement.appendChild(wrapper);
}

function renderMessages() {
    const chat = chats.find(item => item.id === activeChatId);
    messagesElement.replaceChildren();
    welcome.hidden = chat.messages.length > 0;

    chat.messages.forEach(message => addMessage(message.role, message.text));
    conversation.scrollTop = conversation.scrollHeight;
}

function demoAnswer(question) {
    const q = question.toLowerCase();

    if (q.includes("согласован")) {
        return "Демонстрационный ответ.\n\nТиповой процесс согласования может включать подготовку документа, проверку ответственным сотрудником, согласование с уполномоченными лицами и утверждение.\n\nВажно: это пример, а не подтверждённый внутренний регламент.";
    }

    if (q.includes("документ") || q.includes("заявк")) {
        return "Демонстрационный ответ.\n\nСостав документов зависит от типа заявки и внутренних требований организации. В рабочей версии здесь будет информация из подключённых регламентов.\n\nПока конкретный перечень не подтверждён.";
    }

    if (q.includes("шаблон")) {
        return "Демонстрационный ответ.\n\nВ рабочей версии помощник сможет искать подходящие шаблоны документов и показывать ссылки на найденные материалы. Сейчас поиск по реальным файлам ещё не подключён.";
    }

    return "Я получил ваш вопрос: «" + question + "».\n\nСейчас работает демонстрационный режим: нейросеть и база регламентов ещё не подключены. Поэтому я не могу подтвердить ответ ссылкой на внутренний документ.";
}

function sendMessage(text) {
    const question = text.trim();
    if (!question) return;

    const chat = chats.find(item => item.id === activeChatId);
    chat.messages.push({ role: "user", text: question });

    if (chat.messages.length === 1) {
        chat.title = question.length > 30 ? question.slice(0, 30) + "…" : question;
    }

    chat.messages.push({ role: "assistant", text: demoAnswer(question) });

    renderChatList();
    renderMessages();
}

form.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(input.value);
    input.value = "";
    input.style.height = "auto";
    input.focus();
});

input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";
});

input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
    }
});

document.querySelectorAll(".suggestion").forEach(button => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.prompt);
    });
});

document.getElementById("new-chat").addEventListener("click", () => {
    const chat = {
        id: nextId++,
        title: "Новый диалог",
        messages: []
    };

    chats.unshift(chat);
    activeChatId = chat.id;
    renderChatList();
    renderMessages();
    input.focus();
});

document.getElementById("logout").addEventListener("click", () => {
    alert("Авторизация пока не подключена. Сейчас это демонстрационный интерфейс.");
});

renderChatList();
renderMessages();
