<template>
  <div
    class="flex justify-between items-center my-3 sm:mt-8 sm:mb-4 font-medium text-lg"
  >
    <div class="flex items-center h-8 font-semibold text-ink-gray-8 text-xl">
      {{ __('Data') }}
      <Badge
        v-if="document.isDirty"
        class="ml-3"
        label="Não Salvo"
        theme="orange"
      />
    </div>
    <div class="flex gap-1">
      <Button
        v-if="isManager() && !isMobileView"
        :tooltip="__('Edit fields layout')"
        :icon="EditIcon"
        @click="showDataFieldsModal = true"
      />
      <Button
        label="Salvar"
        :disabled="!document.isDirty"
        variant="solid"
        :loading="document.save.loading"
        @click="saveChanges"
      />
    </div>
  </div>
  <div
    v-if="document.get.loading"
    class="flex flex-col flex-1 justify-center items-center gap-3 font-medium text-ink-gray-6 text-xl"
  >
    <LoadingIndicator class="w-6 h-6" />
    <span>{{ __('Loading...') }}</span>
  </div>
  <div v-else class="pb-8">
    <FieldLayout
      v-if="tabs.data"
      :tabs="tabs.data"
      :data="document.doc"
      :doctype="doctype"
    />
  </div>
  <DataFieldsModal
    v-if="showDataFieldsModal"
    v-model="showDataFieldsModal"
    :doctype="doctype"
    @reload="
      () => {
        tabs.reload()
        document.reload()
      }
    "
  />
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import DataFieldsModal from '@/components/Modals/DataFieldsModal.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import { Badge, createResource } from 'frappe-ui'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import { usersStore } from '@/stores/users'
import { useDocument } from '@/data/document'
import { isMobileView } from '@/composables/settings'
import { ref, watch, getCurrentInstance } from 'vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  docname: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['beforeSave', 'afterSave'])

const { isManager } = usersStore()

const instance = getCurrentInstance()
const attrs = instance?.vnode?.props ?? {}

const showDataFieldsModal = ref(false)

const { document } = useDocument(props.doctype, props.docname)

const tabs = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['DataFields', props.doctype],
  params: { doctype: props.doctype, type: 'Data Fields' },
  auto: true,
})

function saveChanges() {
  if (!document.isDirty) return

  const updatedDoc = { ...document.doc }
  const oldDoc = { ...document.originalDoc }

  const changes = Object.keys(updatedDoc).reduce((acc, key) => {
    if (JSON.stringify(updatedDoc[key]) !== JSON.stringify(oldDoc[key])) {
      acc[key] = updatedDoc[key]
    }
    return acc
  }, {})

  const hasListener = attrs['onBeforeSave'] !== undefined

  if (hasListener) {
    emit('beforeSave', changes)
  } else {
    document.save.submit(null, {
      onSuccess: () => emit('afterSave', changes),
    })
  }
}

watch(
  () => document.doc,
  (newValue, oldValue) => {
    if (!oldValue) return
    if (newValue && oldValue) {
      const isDirty =
        JSON.stringify(newValue) !== JSON.stringify(document.originalDoc)
      document.isDirty = isDirty
      if (isDirty) {
        document.save.loading = false
      }
    }
  },
  { deep: true },
)
</script>
