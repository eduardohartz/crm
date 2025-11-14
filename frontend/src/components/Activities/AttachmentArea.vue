<template>
  <div v-if="attachments.length">
    <div v-for="(attachment, i) in attachments" :key="attachment.name">
      <div
        class="flex justify-between gap-2 hover:bg-surface-menu-bar p-2.5 rounded text-base cursor-pointer activity"
        @click="openFile(attachment)"
      >
        <div class="flex gap-2 truncate">
          <div
            class="flex flex-shrink-0 justify-center items-center bg-surface-white rounded size-11 overflow-hidden"
            :class="{ border: !isImage(attachment.file_type) }"
          >
            <img
              v-if="isImage(attachment.file_type)"
              class="size-full object-cover"
              :src="attachment.file_url"
              :alt="attachment.file_name"
            />
            <component
              v-else
              class="size-4 text-ink-gray-7"
              :is="fileIcon(attachment.file_type)"
            />
          </div>
          <div class="flex flex-col justify-center gap-1 truncate">
            <div class="text-ink-gray-8 text-base truncate">
              {{ attachment.file_name }}
            </div>
            <div class="mb-1 text-ink-gray-5 text-sm">
              {{ convertSize(attachment.file_size) }}
            </div>
          </div>
        </div>
        <div class="flex flex-col flex-shrink-0 items-end gap-2">
          <Tooltip :text="formatDate(attachment.creation)">
            <div class="text-ink-gray-5 text-sm">
              {{ __(timeAgo(attachment.creation)) }}
            </div>
          </Tooltip>
          <div class="flex gap-1">
            <Button
              :tooltip="
                attachment.is_private ? __('Make public') : __('Make private')
              "
              class="!size-5"
              @click.stop="
                togglePrivate(attachment.name, attachment.is_private)
              "
            >
              <template #icon>
                <FeatherIcon
                  :name="attachment.is_private ? 'lock' : 'unlock'"
                  class="size-3 text-ink-gray-7"
                />
              </template>
            </Button>
            <Button
              :tooltip="__('Delete attachment')"
              class="!size-5"
              @click.stop="() => deleteAttachment(attachment.name)"
            >
              <template #icon>
                <FeatherIcon name="trash-2" class="size-3 text-ink-gray-7" />
              </template>
            </Button>
          </div>
        </div>
      </div>
      <div
        v-if="i < attachments.length - 1"
        class="mx-2 border-t border-outline-gray-modals h-px"
      />
    </div>
  </div>
</template>
<script setup>
import FileAudioIcon from '@/components/Icons/FileAudioIcon.vue'
import FileTextIcon from '@/components/Icons/FileTextIcon.vue'
import FileVideoIcon from '@/components/Icons/FileVideoIcon.vue'
import { globalStore } from '@/stores/global'
import { call, Tooltip } from 'frappe-ui'
import { formatDate, timeAgo, convertSize, isImage } from '@/utils'

const props = defineProps({
  attachments: Array,
})

const emit = defineEmits(['reload'])

const { $dialog } = globalStore()

function openFile(attachment) {
  window.open(attachment.file_url, '_blank')
}

function togglePrivate(fileName, isPrivate) {
  let changeTo = isPrivate ? __('public') : __('private')
  let title = __('Make attachment {0}', [changeTo])
  let message = `Você tem certeza que deseja tornar este anexo ${changeTo}?`
  $dialog({
    title,
    message,
    actions: [
      {
        label: __('Make {0}', [changeTo]),
        variant: 'solid',
        onClick: async (close) => {
          await call('frappe.client.set_value', {
            doctype: 'File',
            name: fileName,
            fieldname: {
              is_private: !isPrivate,
            },
          })
          emit('reload')
          close()
        },
      },
    ],
  })
}

function deleteAttachment(fileName) {
  $dialog({
    title: __('Delete attachment'),
    message: __('Are you sure you want to delete this attachment?'),
    actions: [
      {
        label: __('Delete'),
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          await call('frappe.client.delete', {
            doctype: 'File',
            name: fileName,
          })
          emit('reload')
          close()
        },
      },
    ],
  })
}

function fileIcon(type) {
  if (!type) return FileTextIcon
  let audioExtentions = ['wav', 'mp3', 'ogg', 'flac', 'aac']
  let videoExtentions = ['mp4', 'avi', 'mkv', 'flv', 'mov']
  if (audioExtentions.includes(type.toLowerCase())) {
    return FileAudioIcon
  } else if (videoExtentions.includes(type.toLowerCase())) {
    return FileVideoIcon
  }
  return FileTextIcon
}
</script>
