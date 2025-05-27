<template>
  <div class="chat-interface">
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <div class="message-content">
          {{ message.content }}
        </div>
        <div
          v-if="message.clarificationQuestion"
          class="clarification-prompt"
        >
          <div class="clarification-icon">?</div>
          <div class="clarification-text">
            {{ message.clarificationQuestion }}
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <input
        v-model="userInput"
        @keyup.enter="sendMessage"
        :placeholder="inputPlaceholder"
        :disabled="isProcessing"
      />
      <button
        @click="sendMessage"
        :disabled="isProcessing"
      >
        {{ isProcessing ? 'Processing...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed } from 'vue'
import axios from 'axios'

export default {
    name: 'ChatInterface',
    props: {
        flightData: {
            type: Object,
            default: () => ({})
        }
    },
    setup (props) {
        const messages = ref([])
        const userInput = ref('')
        const isProcessing = ref(false)
        const messagesContainer = ref(null)
        const sessionId = ref(Date.now().toString())
        const needsClarification = ref(false)
        const clarificationQuestion = ref('')

        const scrollToBottom = async () => {
            await nextTick()
            if (messagesContainer.value) {
                messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
            }
        }

        const sendMessage = async () => {
            if (!userInput.value.trim() || isProcessing.value) return

            const userMessage = {
                role: 'user',
                content: userInput.value
            }
            messages.value.push(userMessage)
            userInput.value = ''
            isProcessing.value = true

            try {
                const response = await axios.post('http://localhost:8000/api/chat', {
                    messages: [userMessage],
                    flightData: props.flightData,
                    sessionId: sessionId.value
                })

                const assistantMessage = {
                    role: 'assistant',
                    content: response.data.response,
                    clarificationQuestion: response.data.clarificationQuestion
                }
                messages.value.push(assistantMessage)

                if (response.data.needsClarification) {
                    needsClarification.value = true
                    clarificationQuestion.value = response.data.clarificationQuestion
                } else {
                    needsClarification.value = false
                    clarificationQuestion.value = ''
                }
            } catch (error) {
                console.error('Error sending message:', error)
                messages.value.push({
                    role: 'assistant',
                    content: 'Sorry, I encountered an error. Please try again.',
                    isError: true
                })
            } finally {
                isProcessing.value = false
                scrollToBottom()
            }
        }

        const inputPlaceholder = computed(() => {
            if (needsClarification.value) {
                return `Please respond to: ${clarificationQuestion.value}`
            }
            return 'Ask about your flight data...'
        })

        onMounted(() => {
            messages.value.push({
                role: 'assistant',
                content: 'Hello! I\'m your UAV flight data analyst. I can help you understand your flight logs and ' +
                    'telemetry data. What would you like to know?'
            })
        })

        return {
            messages,
            userInput,
            isProcessing,
            messagesContainer,
            sendMessage,
            inputPlaceholder
        }
    }
}
</script>

<style scoped>
.chat-interface {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    height: 80vh;
    width: 80vw;
    max-width: 800px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px 8px 0 0;
}

.chat-input {
    display: flex;
    padding: 15px;
    background: white;
    border-top: 1px solid #eee;
    border-radius: 0 0 8px 8px;
}

.chat-input input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-right: 10px;
}

.chat-input button {
    padding: 10px 20px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.chat-input button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.message {
    margin-bottom: 15px;
    max-width: 80%;
}

.message.user {
    margin-left: auto;
}

.message-content {
    padding: 10px 15px;
    border-radius: 15px;
    background: #fff;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.message.user .message-content {
    background: #007bff;
    color: white;
}

.message.assistant .message-content {
    background: #e9ecef;
}

.clarification-prompt {
    display: flex;
    align-items: center;
    margin-top: 10px;
    padding: 10px;
    background: #fff3cd;
    border-radius: 8px;
    border: 1px solid #ffeeba;
}

.clarification-icon {
    width: 24px;
    height: 24px;
    background: #ffc107;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
}

.clarification-text {
    color: #856404;
}
</style>
