<template>
  <Popover placement="bottom-end">
    <template #target="{ togglePopover }">
      <Button :label="__('Columns')" @click="togglePopover">
        <template v-if="hideLabel">
          <ColumnsIcon class="h-4" />
        </template>
        <template v-if="!hideLabel" #prefix>
          <ColumnsIcon class="h-4" />
        </template>
      </Button>
    </template>
    <template #body="{ close }">
      <div
        class="bg-surface-modal ring-opacity-5 shadow-2xl my-2 p-1.5 rounded-lg focus:outline-none ring-1 ring-black min-w-40"
      >
        <div v-if="!edit">
          <Draggable
            :list="columns"
            @end="apply"
            :delay="isTouchScreenDevice() ? 200 : 0"
            item-key="key"
            class="list-group"
          >
            <template #item="{ element }">
              <div
                class="flex justify-between items-center gap-6 hover:bg-surface-gray-2 px-2 py-1.5 rounded text-ink-gray-8 text-base cursor-grab"
              >
                <div class="flex items-center gap-2">
                  <DragIcon class="h-3.5" />
                  <div>{{ __(element.label) }}</div>
                </div>
                <div class="flex items-center gap-0.5 cursor-pointer">
                  <Button
                    variant="ghost"
                    class="!p-1 w-5 !h-5"
                    @click="editColumn(element)"
                  >
                    <template #icon>
                      <EditIcon class="h-3.5" />
                    </template>
                  </Button>
                  <Button
                    variant="ghost"
                    class="!p-1 w-5 !h-5"
                    @click="removeColumn(element)"
                  >
                    <template #icon>
                      <FeatherIcon name="x" class="h-3.5" />
                    </template>
                  </Button>
                </div>
              </div>
            </template>
          </Draggable>
          <div
            class="flex flex-col gap-1 mt-1.5 pt-1.5 border-t border-outline-gray-modals"
          >
            <Autocomplete
              value=""
              :options="fields"
              @change="(e) => addColumn(e)"
            >
              <template #target="{ togglePopover }">
                <Button
                  class="!justify-start w-full !text-ink-gray-5"
                  variant="ghost"
                  :label="__('Add Column')"
                  iconLeft="plus"
                  @click="togglePopover"
                />
              </template>
            </Autocomplete>
            <Button
              v-if="columnsUpdated"
              class="!justify-start w-full !text-ink-gray-5"
              variant="ghost"
              :label="__('Reset Changes')"
              :iconLeft="ReloadIcon"
              @click="reset(close)"
            />
            <Button
              v-if="!is_default"
              class="!justify-start w-full !text-ink-gray-5"
              variant="ghost"
              label="Resetar para Padrão"
              :iconLeft="ReloadIcon"
              @click="resetToDefault(close)"
            />
          </div>
        </div>
        <div v-else>
          <div
            class="flex flex-col justify-between items-center gap-2 px-2 py-1.5 rounded text-ink-gray-8 text-base"
          >
            <div class="flex flex-col items-center gap-3">
              <FormControl
                type="text"
                size="md"
                :label="__('Label')"
                v-model="column.label"
                class="w-52 sm:w-full"
                :placeholder="__('First Name')"
              />
              <FormControl
                type="text"
                size="md"
                :label="__('Width')"
                class="w-52 sm:w-full"
                v-model="column.width"
                placeholder="10rem"
                :description="
                  __(
                    'Width can be in number, pixel or rem (eg. 3, 30px, 10rem)',
                  )
                "
                :debounce="500"
              />
            </div>
            <div class="flex gap-2 pt-2 border-t w-full">
              <Button
                variant="subtle"
                :label="__('Cancel')"
                class="flex-1 w-full"
                @click="cancelUpdate"
              />
              <Button
                variant="solid"
                :label="__('Update')"
                class="flex-1 w-full"
                @click="updateColumn(column)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import ColumnsIcon from '@/components/Icons/ColumnsIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import DragIcon from '@/components/Icons/DragIcon.vue'
import ReloadIcon from '@/components/Icons/ReloadIcon.vue'
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import { isTouchScreenDevice } from '@/utils'
import { Popover } from 'frappe-ui'
import Draggable from 'vuedraggable'
import { computed, ref } from 'vue'
import { watchOnce } from '@vueuse/core'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  hideLabel: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update'])
const columnsUpdated = ref(false)

const oldValues = ref({
  columns: [],
  rows: [],
  isDefault: false,
})

const list = defineModel()
const edit = ref(false)
const column = ref({
  old: {},
  label: '',
  key: '',
  width: '10rem',
})

const is_default = computed({
  get: () => list.value?.data?.is_default,
  set: (val) => {
    list.value.data.is_default = val
  },
})

const columns = computed({
  get: () => list.value?.data?.columns,
  set: (val) => {
    list.value.data.columns = val
  },
})

const rows = computed({
  get: () => list.value?.data?.rows,
  set: (val) => {
    list.value.data.rows = val
  },
})

const fields = computed(() => {
  let allFields = list.value?.data?.fields
  if (!allFields) return []

  return allFields.filter((field) => {
    return !columns.value.find((column) => column.key === field.fieldname)
  })
})

function addColumn(c) {
  if (!c) return
  let align = ['Float', 'Int', 'Percent', 'Currency'].includes(c.type)
    ? 'right'
    : 'left'
  let _column = {
    label: c.label,
    type: c.fieldtype,
    key: c.fieldname,
    width: '10rem',
    align,
  }
  columns.value.push(_column)
  rows.value.push(c.value)
  apply(true)
}

function removeColumn(c) {
  columns.value = columns.value.filter((column) => column.key !== c.key)
  if (c.key !== 'name') {
    rows.value = rows.value.filter((row) => row !== c.key)
  }
  apply()
}

function editColumn(c) {
  edit.value = true
  column.value = c
  column.value.old = { ...c }
}

function updateColumn(c) {
  edit.value = false
  let index = columns.value.findIndex((column) => column.key === c.key)
  columns.value[index].label = c.label
  columns.value[index].width = c.width

  if (columns.value[index].old) {
    delete columns.value[index].old
  }
  apply()
}

function cancelUpdate() {
  edit.value = false
  column.value.label = column.value.old.label
  column.value.width = column.value.old.width
  delete column.value.old
}

function reset(close) {
  apply(true, false, true)
  close()
}

function resetToDefault(close) {
  apply(true, true)
  close()
}

function apply(reload = false, isDefault = false, reset = false) {
  is_default.value = isDefault
  columnsUpdated.value = true
  let obj = {
    columns: reset ? oldValues.value.columns : columns.value,
    rows: reset ? oldValues.value.rows : rows.value,
    isDefault: reset ? oldValues.value.isDefault : isDefault,
    reload,
    reset,
  }
  emit('update', obj)

  if (reload) {
    // will have think of a better way to do this
    setTimeout(() => {
      is_default.value = reset ? oldValues.value.isDefault : isDefault
      columnsUpdated.value = !reset
    }, 100)
  }
}

watchOnce(
  () => list.value.data,
  (val) => {
    if (!val) return
    oldValues.value.columns = JSON.parse(JSON.stringify(val.columns))
    oldValues.value.rows = JSON.parse(JSON.stringify(val.rows))
    oldValues.value.isDefault = val.is_default
  },
)
</script>
