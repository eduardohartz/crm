<template>
  <Autocomplete
    v-if="!sortValues?.size"
    :options="options"
    value=""
    :placeholder="__('First Name')"
    @change="(e) => setSort(e)"
  >
    <template #target="{ togglePopover }">
      <Button :label="__('Sort')" @click="togglePopover()">
        <template v-if="hideLabel">
          <SortIcon class="h-4" />
        </template>
        <template v-if="!hideLabel && !sortValues?.size" #prefix>
          <SortIcon class="h-4" />
        </template>
      </Button>
    </template>
  </Autocomplete>
  <Popover placement="bottom-end" v-else>
    <template #target="{ isOpen, togglePopover }">
      <Button
        v-if="sortValues.size > 1"
        :label="__('Sort')"
        :icon="hideLabel && SortIcon"
        :iconLeft="!hideLabel && SortIcon"
        @click="togglePopover"
      >
        <template v-if="sortValues?.size" #suffix>
          <div
            class="flex justify-center items-center bg-surface-white shadow-sm pt-px rounded-[5px] w-5 h-5 font-medium text-ink-gray-8 text-xs"
          >
            {{ sortValues.size }}
          </div>
        </template>
      </Button>
      <div v-else class="flex justify-center items-center">
        <Button
          v-if="sortValues.size"
          class="border-r rounded-r-none"
          :icon="
            Array.from(sortValues)[0].direction == 'asc'
              ? AscendingIcon
              : DesendingIcon
          "
          @click.stop="
            () => {
              Array.from(sortValues)[0].direction =
                Array.from(sortValues)[0].direction == 'asc' ? 'desc' : 'asc'
              apply()
            }
          "
        />
        <Button
          :label="getSortLabel()"
          class="[&_svg]:text-ink-gray-5 shrink-0"
          :iconLeft="!hideLabel && !sortValues?.size && SortIcon"
          :iconRight="
            sortValues?.size && (isOpen ? 'chevron-up' : 'chevron-down')
          "
          :class="sortValues.size ? 'rounded-l-none' : ''"
          @click.stop="togglePopover"
        />
      </div>
    </template>
    <template #body="{ close }">
      <div
        class="bg-surface-modal ring-opacity-5 shadow-2xl my-2 rounded-lg focus:outline-none ring-1 ring-black min-w-40"
      >
        <div class="p-2 min-w-60">
          <div
            v-if="sortValues?.size"
            id="sort-list"
            class="flex flex-col gap-2 mb-3"
          >
            <div
              v-for="(sort, i) in sortValues"
              :key="sort.fieldname"
              class="flex items-center gap-1"
            >
              <div class="flex justify-center items-center w-7 h-7 handle">
                <DragIcon class="w-4 h-4 text-ink-gray-5 cursor-grab" />
              </div>
              <div class="flex flex-1">
                <Button
                  size="md"
                  class="border-r rounded-r-none"
                  :icon="
                    sort.direction == 'asc' ? AscendingIcon : DesendingIcon
                  "
                  @click="
                    () => {
                      sort.direction = sort.direction == 'asc' ? 'desc' : 'asc'
                      apply()
                    }
                  "
                />
                <Autocomplete
                  class="[&>_div]:w-full"
                  :value="sort.fieldname"
                  :options="sortOptions.data"
                  @change="(e) => updateSort(e, i)"
                  :placeholder="__('First Name')"
                >
                  <template
                    #target="{
                      open,
                      togglePopover,
                      selectedValue,
                      displayValue,
                    }"
                  >
                    <Button
                      class="flex justify-between items-center rounded-l-none w-full !text-ink-gray-5"
                      size="md"
                      :label="displayValue(selectedValue)"
                      :iconRight="open ? 'chevron-down' : 'chevron-up'"
                      @click="togglePopover()"
                    />
                  </template>
                </Autocomplete>
              </div>
              <Button variant="ghost" icon="x" @click="removeSort(i)" />
            </div>
          </div>
          <div
            v-else
            class="flex items-center mb-3 px-3 h-7 text-ink-gray-5 text-sm"
          >
            Vazio - Escolha um campo para filtrar
          </div>
          <div class="flex justify-between items-center gap-2">
            <Autocomplete
              :options="options"
              value=""
              :placeholder="__('First Name')"
              @change="(e) => setSort(e)"
            >
              <template #target="{ togglePopover }">
                <Button
                  class="!text-ink-gray-5"
                  :label="__('Add Sort')"
                  variant="ghost"
                  iconLeft="plus"
                  @click="togglePopover()"
                />
              </template>
            </Autocomplete>
            <Button
              v-if="sortValues?.size"
              class="!text-ink-gray-5"
              variant="ghost"
              :label="__('Clear Sort')"
              @click="clearSort(close)"
            />
          </div>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import AscendingIcon from '@/components/Icons/AscendingIcon.vue'
import DesendingIcon from '@/components/Icons/DesendingIcon.vue'
import SortIcon from '@/components/Icons/SortIcon.vue'
import DragIcon from '@/components/Icons/DragIcon.vue'
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import { useSortable } from '@vueuse/integrations/useSortable'
import { createResource, Popover } from 'frappe-ui'
import { computed, nextTick, onMounted } from 'vue'

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
const list = defineModel()

const sortOptions = createResource({
  url: 'crm.api.doc.sort_options',
  cache: ['sortOptions', props.doctype],
  params: { doctype: props.doctype },
})

onMounted(() => {
  if (sortOptions.data?.length) return
  sortOptions.fetch()
})

const sortValues = computed({
  get: () => {
    if (!list.value?.data) return new Set()
    let allSortValues = list.value?.params?.order_by
    if (!allSortValues || !sortOptions.data) return new Set()
    if (allSortValues.trim() === 'modified desc') return new Set()
    allSortValues = allSortValues.split(', ').map((sortValue) => {
      const [fieldname, direction] = sortValue.split(' ')
      return { fieldname, direction }
    })
    return new Set(allSortValues)
  },
  set: (value) => {
    list.value.params.order_by = convertToString(value)
  },
})

const options = computed(() => {
  if (!sortOptions.data) return []
  if (!sortValues.value.size) return sortOptions.data
  const selectedOptions = [...sortValues.value].map((sort) => sort.fieldname)
  restartSort()
  return sortOptions.data.filter((option) => {
    return !selectedOptions.includes(option.fieldname)
  })
})

const sortSortable = useSortable('#sort-list', sortValues, {
  handle: '.handle',
  animation: 200,
  onEnd: () => apply(),
})

function getSortLabel() {
  if (!sortValues.value.size) return __('Sort')
  let values = Array.from(sortValues.value)
  let label = sortOptions.data?.find(
    (option) => option.fieldname === values[0].fieldname,
  )?.label
  return label || values[0].fieldname
}

function setSort(data) {
  sortValues.value.add({ fieldname: data.fieldname, direction: 'asc' })
  restartSort()
  apply()
}

function updateSort(data, index) {
  let oldSort = Array.from(sortValues.value)[index]
  sortValues.value.delete(oldSort)
  sortValues.value.add({
    fieldname: data.fieldname,
    direction: oldSort.direction,
  })
  apply()
}

function removeSort(index) {
  sortValues.value.delete(Array.from(sortValues.value)[index])
  apply()
}

function clearSort(close) {
  sortValues.value.clear()
  apply()
  close()
}

function apply() {
  nextTick(() => {
    emit('update', convertToString(sortValues.value))
  })
}

function convertToString(values) {
  let _sortValues = ''
  values.forEach((f) => {
    _sortValues += `${f.fieldname} ${f.direction}, `
  })
  _sortValues = _sortValues.slice(0, -2)
  return _sortValues
}

function restartSort() {
  sortSortable.stop()
  sortSortable.start()
}
</script>
