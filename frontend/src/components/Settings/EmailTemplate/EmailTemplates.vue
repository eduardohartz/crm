<template>
  <div class="flex flex-col gap-6 p-6 h-full text-ink-gray-8">
    <!-- Header -->
    <div class="flex justify-between px-2 pt-2">
      <div class="flex flex-col gap-1 w-9/12">
        <h2 class="flex gap-2 h-5 font-semibold text-xl leading-none">
          Templates de email
        </h2>
        <p class="text-ink-gray-6 text-p-base">
          {{
            __(
              'Add, edit, and manage email templates for various CRM communications',
            )
          }}
        </p>
      </div>
      <div class="flex justify-end space-x-2 w-3/12 item-center">
        <Button
          :label="__('New')"
          icon-left="plus"
          variant="solid"
          @click="emit('updateStep', 'new-template')"
        />
      </div>
    </div>

    <!-- loading state -->
    <div
      v-if="templates.loading"
      class="flex justify-between mt-28 w-full h-full"
    >
      <Button
        :loading="templates.loading"
        variant="ghost"
        class="w-full"
        size="2xl"
      />
    </div>

    <!-- Empty State -->
    <div
      v-if="!templates.loading && !templates.data?.length"
      class="flex justify-between w-full h-full"
    >
      <div
        class="flex justify-center items-center border border-dashed rounded w-full text-ink-gray-4"
      >
        Nenhum template de email encontrado.
      </div>
    </div>

    <!-- Email template list -->
    <div
      class="flex flex-col overflow-hidden"
      v-if="!templates.loading && templates.data?.length"
    >
      <div
        v-if="templates.data?.length > 10"
        class="flex justify-between items-center mb-4 px-2 pt-0.5"
      >
        <TextInput
          ref="searchRef"
          v-model="search"
          :placeholder="__('Search template')"
          class="w-1/3"
          :debounce="300"
        >
          <template #prefix>
            <FeatherIcon name="search" class="w-4 h-4 text-ink-gray-6" />
          </template>
        </TextInput>
        <FormControl
          type="select"
          v-model="currentDoctype"
          :options="[
            { label: __('All'), value: 'All' },
            { label: __('Lead'), value: 'CRM Lead' },
            { label: __('Deal'), value: 'CRM Deal' },
          ]"
        />
      </div>
      <div class="flex items-center px-4 py-2 text-ink-gray-5 text-sm">
        <div class="w-4/6">{{ __('Template name') }}</div>
        <div class="w-1/6">{{ __('For') }}</div>
        <div class="w-1/6">{{ __('Enabled') }}</div>
      </div>
      <div class="mx-4 border-t border-outline-gray-modals h-px" />
      <ul class="px-2 overflow-y-auto">
        <template v-for="(template, i) in templatesList" :key="template.name">
          <li
            class="flex justify-between items-center hover:bg-surface-menu-bar p-3 rounded cursor-pointer"
            @click="() => emit('updateStep', 'edit-template', { ...template })"
          >
            <div class="flex flex-col pr-5 w-4/6">
              <div class="font-medium text-ink-gray-7 text-p-base truncate">
                {{ template.name }}
              </div>
              <div class="text-ink-gray-5 text-p-sm truncate">
                {{ template.subject }}
              </div>
            </div>
            <div class="w-1/6 text-ink-gray-6 text-base">
              {{ template.reference_doctype.replace('CRM ', '') }}
            </div>
            <div class="flex justify-between items-center w-1/6">
              <Switch
                size="sm"
                v-model="template.enabled"
                @update:model-value="toggleEmailTemplate(template)"
                @click.stop
              />
              <Dropdown
                class=""
                :options="getDropdownOptions(template)"
                placement="right"
                :button="{
                  icon: 'more-horizontal',
                  variant: 'ghost',
                  onblur: (e) => {
                    e.stopPropagation()
                    confirmDelete = false
                  },
                }"
                @click.stop
              />
            </div>
          </li>
          <div
            v-if="templatesList.length !== i + 1"
            class="mx-2 border-t border-outline-gray-modals h-px"
          />
        </template>
        <!-- Load More Button -->
        <div
          v-if="!templates.loading && templates.hasNextPage"
          class="flex justify-center"
        >
          <Button
            class="mt-3.5 p-2"
            @click="() => templates.next()"
            :loading="templates.loading"
            :label="__('Load More')"
            icon-left="refresh-cw"
          />
        </div>
      </ul>
    </div>
  </div>
</template>
<script setup>
import {
  TextInput,
  FormControl,
  Switch,
  Dropdown,
  FeatherIcon,
  toast,
} from 'frappe-ui'
import { ref, computed, inject } from 'vue'

const emit = defineEmits(['updateStep'])

const templates = inject('templates')

const search = ref('')
const currentDoctype = ref('All')
const confirmDelete = ref(false)

const templatesList = computed(() => {
  let list = templates.data || []
  if (search.value) {
    list = list.filter(
      (template) =>
        template.name.toLowerCase().includes(search.value.toLowerCase()) ||
        template.subject.toLowerCase().includes(search.value.toLowerCase()),
    )
  }
  if (currentDoctype.value !== 'All') {
    list = list.filter(
      (template) => template.reference_doctype === currentDoctype.value,
    )
  }
  return list
})

function toggleEmailTemplate(template) {
  templates.setValue.submit(
    {
      name: template.name,
      enabled: template.enabled ? 1 : 0,
    },
    {
      onSuccess: () => {
        toast.success(
          template.enabled
            ? __('Template enabled successfully')
            : __('Template disabled successfully'),
        )
      },
      onError: (error) => {
        toast.error(error.messages[0] || __('Failed to update template'))
        // Revert the change if there was an error
        template.enabled = !template.enabled
      },
    },
  )
}

function deleteTemplate(template) {
  confirmDelete.value = false
  templates.delete.submit(template.name, {
    onSuccess: () => {
      toast.success(__('Template deleted successfully'))
    },
    onError: (error) => {
      toast.error(error.messages[0] || __('Failed to delete template'))
    },
  })
}

function getDropdownOptions(template) {
  let options = [
    {
      label: __('Duplicate'),
      icon: 'copy',
      onClick: () => emit('updateStep', 'new-template', { ...template }),
    },
    {
      label: __('Delete'),
      icon: 'trash-2',
      onClick: (e) => {
        e.preventDefault()
        e.stopPropagation()
        confirmDelete.value = true
      },
      condition: () => !confirmDelete.value,
    },
    {
      label: __('Confirm Delete'),
      icon: 'trash-2',
      theme: 'red',
      onClick: () => deleteTemplate(template),
      condition: () => confirmDelete.value,
    },
  ]

  return options
}
</script>
