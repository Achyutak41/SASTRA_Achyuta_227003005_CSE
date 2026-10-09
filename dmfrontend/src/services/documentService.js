import api from "./api";


const documentService = {
  async uploadDocument(file) {
    const formData =
      new FormData();

    formData.append(
      "file",
      file
    );

    const response =
      await api.post(
        "/documents/upload",
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data"
          }
        }
      );

    return response.data;
  },


  async getDocuments() {
    const response =
      await api.get(
        "/documents"
      );

    return response.data;
  },


  async getDocument(
    documentId
  ) {
    const response =
      await api.get(
        `/documents/${documentId}`
      );

    return response.data;
  },


  async deleteDocument(
    documentId
  ) {
    const response =
      await api.delete(
        `/documents/${documentId}`
      );

    return response.data;
  }
};


export default documentService;