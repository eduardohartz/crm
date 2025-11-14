<template>
  <div
    v-if="reply?.message"
    class="flex justify-around items-center gap-2 px-3 sm:px-10 pt-2"
  >
    <div
      class="flex-1 bg-surface-gray-2 mb-1 ml-13 p-2 border-0 border-green-500 border-l-4 rounded text-ink-gray-5 text-base cursor-pointer"
      :class="reply.type == 'Incoming' ? 'border-green-500' : 'border-blue-400'"
    >
      <div
        class="mb-1 font-bold text-sm"
        :class="reply.type == 'Incoming' ? 'text-ink-green-2' : 'text-ink-blue-link'"
      >
        {{ reply.from_name || __('You') }}
      </div>
      <div class="max-h-12 overflow-hidden" v-html="reply.message" />
    </div>

    <Button variant="ghost" icon="x" @click="reply = {}" />
  </div>
  <div class="flex items-end gap-2 px-3 sm:px-10 py-2.5" v-bind="$attrs">
    <div class="flex items-center gap-2 h-8">
      <FileUploader @success="(file) => uploadFile(file)">
        <template v-slot="{ openFileSelector }">
          <div class="flex items-center space-x-2">
            <Dropdown :options="uploadOptions(openFileSelector)">
              <FeatherIcon
                name="plus"
                class="size-4.5 text-ink-gray-5 cursor-pointer"
              />
            </Dropdown>
          </div>
        </template>
      </FileUploader>
      <IconPicker
        v-model="emoji"
        v-slot="{ togglePopover }"
        @update:modelValue="
          () => {
            content += emoji
            $refs.textareaRef.el.focus()
            capture('whatsapp_emoji_added')
          }
        "
      >
        <SmileIcon
          @click="togglePopover"
          class="flex rounded-sm size-4.5 text-ink-gray-4 text-xl leading-none cursor-pointer"
        />
      </IconPicker>
    </div>
    <Textarea
      ref="textareaRef"
      type="textarea"
      class="w-full min-h-8"
      :rows="rows"
      v-model="content"
      :placeholder="placeholder"
      @focus="rows = 6"
      @blur="rows = 1"
      @keydown.enter.stop="(e) => sendTextMessage(e)"
    />
  </div>
</template>

<script setup>
import IconPicker from '@/components/IconPicker.vue'
import SmileIcon from '@/components/Icons/SmileIcon.vue'
import { capture } from '@/telemetry'
import { createResource, Textarea, FileUploader, Dropdown } from 'frappe-ui'
import { ref, nextTick, watch } from 'vue'

const props = defineProps({
  doctype: String,
})

const doc = defineModel()
const whatsapp = defineModel('whatsapp')
const reply = defineModel('reply')
const rows = ref(1)
const textareaRef = ref(null)
const emoji = ref('')

const content = ref('')
const placeholder = ref('Escreva sua mensagem aqui... Pressione Enter para enviar.')
const fileType = ref('')

function show() {
  nextTick(() => textareaRef.value.el.focus())
}

function uploadFile(file) {
  whatsapp.value.attach = file.file_url
  whatsapp.value.content_type = fileType.value
  sendWhatsAppMessage()
  capture('whatsapp_upload_file')
}

function sendTextMessage(event) {
  if (event.shiftKey) return
  sendWhatsAppMessage()
  textareaRef.value.el?.blur()
  content.value = ''
  capture('whatsapp_send_message')
}

async function sendWhatsAppMessage() {
  let args = {
    reference_doctype: props.doctype,
    reference_name: doc.value.name,
    message: content.value,
    to: doc.value.mobile_no,
    attach: whatsapp.value.attach || '',
    reply_to: reply.value?.name || '',
    content_type: whatsapp.value.content_type,
  }
  content.value = ''
  fileType.value = ''
  whatsapp.value.attach = ''
  whatsapp.value.content_type = 'text'
  reply.value = {}
  createResource({
    url: 'crm.api.whatsapp.create_whatsapp_message',
    params: args,
    auto: true,
  })
}

function uploadOptions(openFileSelector) {
  return [
    {
      label: __('Upload Document'),
      icon: 'file',
      onClick: () => {
        fileType.value = 'document'
        openFileSelector()
      },
    },
    {
      label: __('Upload Image'),
      icon: 'image',
      onClick: () => {
        fileType.value = 'image'
        openFileSelector('image/*')
      },
    },
    {
      label: __('Upload Video'),
      icon: 'video',
      onClick: () => {
        fileType.value = 'video'
        openFileSelector('video/*')
      },
    },
  ]
}

watch(reply, (value) => {
  if (value?.message) {
    show()
  }
})

defineExpose({ show })
</script>
