<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Notes" />
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createNote"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="notes"
    v-model:loadMore="loadMore"
    v-model:updatedPageCount="updatedPageCount"
    doctype="FCRM Note"
    :options="{
      hideColumnsButton: true,
      defaultViewName: 'Visão geral',
    }"
  />
  <div class="flex-1 overflow-y-auto">
    <div
      v-if="notes.data?.data?.length"
      class="gap-2 sm:gap-4 grid grid-cols-1 sm:grid-cols-4 px-3 sm:px-5 pb-2 sm:pb-3"
    >
      <div
        v-for="note in notes.data.data"
        class="group flex flex-col justify-between gap-2 hover:bg-surface-menu-bar shadow-sm px-5 py-4 border rounded-lg h-56 cursor-pointer"
        @click="editNote(note)"
      >
        <div class="flex justify-between items-center">
          <div class="font-medium text-ink-gray-9 text-lg truncate">
            {{ note.title }}
          </div>
          <Dropdown
            :options="[
              {
                label: __('Delete'),
                icon: 'trash-2',
                onClick: () => deleteNote(note.name),
              },
            ]"
          >
            <Button
              icon="more-horizontal"
              variant="ghosted"
              class="hover:bg-surface-white"
              @click.stop
            />
          </Dropdown>
        </div>
        <TextEditor
          v-if="note.content"
          :content="note.content"
          :editable="false"
          editor-class="prose-sm text-p-sm max-w-none text-ink-gray-5 focus:outline-none"
          class="flex-1 overflow-hidden"
        />
        <div class="flex justify-between items-center gap-2 mt-2">
          <div class="flex items-center gap-2">
            <UserAvatar :user="note.owner" size="xs" />
            <div class="text-ink-gray-8 text-sm">
              {{ getUser(note.owner).full_name }}
            </div>
          </div>
          <Tooltip :text="formatDate(note.modified)">
            <div class="text-ink-gray-7 text-sm">
              {{ __(timeAgo(note.modified)) }}
            </div>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
  <ListFooter
    v-if="notes.data?.data?.length"
    class="px-3 sm:px-5 py-2 border-t"
    v-model="notes.data.page_length_count"
    :options="{
      rowCount: notes.data.row_count,
      totalCount: notes.data.total_count,
    }"
    @loadMore="() => loadMore++"
  />
  <div v-else class="flex justify-center items-center h-full">
    <div
      class="flex flex-col items-center gap-3 font-medium text-ink-gray-4 text-xl"
    >
      <NoteIcon class="w-10 h-10" />
      <span>Nenhuma nota encontrada</span>
      <Button label="Criar" iconLeft="plus" @click="createNote" />
    </div>
  </div>
  <NoteModal
    v-model="showNoteModal"
    v-model:reloadNotes="notes"
    :note="currentNote"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { usersStore } from '@/stores/users'
import { timeAgo, formatDate } from '@/utils'
import { TextEditor, call, Dropdown, Tooltip, ListFooter } from 'frappe-ui'
import { ref, watch } from 'vue'

const { getUser } = usersStore()

const showNoteModal = ref(false)
const currentNote = ref(null)

const notes = ref({})
const loadMore = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

watch(
  () => notes.value?.data?.page_length_count,
  (val, old_value) => {
    openNoteFromURL()
    if (!val || val === old_value) return
    updatedPageCount.value = val
  },
)

function createNote() {
  currentNote.value = {
    title: '',
    content: '',
  }
  showNoteModal.value = true
}

function editNote(note) {
  currentNote.value = note
  showNoteModal.value = true
}

async function deleteNote(name) {
  await call('frappe.client.delete', {
    doctype: 'FCRM Note',
    name,
  })
  notes.value.reload()
}

const openNoteFromURL = () => {
  const searchParams = new URLSearchParams(window.location.search)
  const noteName = searchParams.get('open')

  if (noteName && notes.value?.data?.data) {
    const foundNote = notes.value.data.data.find(
      (note) => note.name === noteName,
    )
    if (foundNote) {
      editNote(foundNote)
    }
    searchParams.delete('open')
    window.history.replaceState(null, '', window.location.pathname)
  }
}
</script>
