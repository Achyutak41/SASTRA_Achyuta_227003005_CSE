import api from "./api";

const chatService = {
  async getChats() {
    const response = await api.get(
      "/chats"
    );

    return response.data;
  },

  async getChat(chatId) {
    const response = await api.get(
      `/chats/${chatId}`
    );

    return response.data;
  },

  async createChat(data = {}) {
    const response = await api.post(
      "/chats",
      data
    );

    return response.data;
  },

  async sendMessage(data) {
    const response = await api.post(
      "/chat",
      data
    );

    return response.data;
  },

  async deleteChat(chatId) {
    const response = await api.delete(
      `/chats/${chatId}`
    );

    return response.data;
  }
};

export default chatService;