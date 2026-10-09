import { useChatContext } from "../context/ChatContext";

function useChat() {
  return useChatContext();
}

export default useChat;