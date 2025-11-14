<template>
  <div
    class="group flex justify-between items-center bg-transparent hover:bg-surface-gray-3 active:bg-surface-gray-4 p-1 pl-2 rounded w-full text-ink-gray-8 text-base transition-colors"
  >
    <div class="flex flex-1 justify-between items-center gap-7">
      <div v-show="!editMode">{{ option.value }}</div>
      <TextInput
        ref="inputRef"
        v-show="editMode"
        v-model="option.value"
        class="w-full"
        :placeholder="option.placeholder"
        @blur.stop="saveOption"
        @keydown.enter.stop="(e) => e.target.blur()"
      />

      <div class="flex justify-center items-center actions">
        <Button
          v-if="editMode"
          variant="ghost"
          :label="`Salvar`"
          class="hover:bg-surface-gray-4 opacity-0 group-hover:opacity-100"
          @click="saveOption"
        />
        <Button
          v-if="!isNew && !option.selected"
          :tooltip="__('Set As Primary')"
          variant="ghost"
          :icon="SuccessIcon"
          class="hover:bg-surface-gray-4 opacity-0 group-hover:opacity-100"
          @click="option.onClick"
        />
        <Button
          v-if="!editMode"
          :tooltip="__('Edit')"
          variant="ghost"
          :icon="EditIcon"
          class="hover:bg-surface-gray-4 opacity-0 group-hover:opacity-100"
          @click="toggleEditMode"
        />
        <Button
          :tooltip="__('Delete')"
          variant="ghost"
          icon="x"
          class="hover:bg-surface-gray-4 opacity-0 group-hover:opacity-100"
          @click="() => option.onDelete(option, isNew)"
        />
      </div>
    </div>
    <div v-if="option.selected">
      <FeatherIcon name="check" class="w-6 h-4 text-ink-gray-5" />
    </div>
  </div>
</template>

<script setup>
import SuccessIcon from '@/components/Icons/SuccessIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { TextInput } from 'frappe-ui'
import { nextTick, ref, onMounted } from 'vue'

const props = defineProps({
  option: {
    type: Object,
    default: () => {},
  },
})

const editMode = ref(false)
const isNew = ref(false)
const inputRef = ref(null)

onMounted(() => {
  if (!props.option?.value) {
    editMode.value = true
    isNew.value = true
    nextTick(() => inputRef.value.el.focus())
  }
})

const toggleEditMode = () => {
  editMode.value = !editMode.value
  editMode.value && nextTick(() => inputRef.value.el.focus())
}

const saveOption = (e) => {
  if (!e.target.value) return
  toggleEditMode()
  props.option.onSave(props.option, isNew.value)
  isNew.value = false
}
</script>
