<template>
  <ListView
    :columns="columns"
    :rows="rows"
    :options="{
      onRowClick: (row) => emit('showScheduledCall', row),
      selectable: false,
      showTooltip: true
    }"
    row-key="full_name"
  >
    <ListRows class="mx-3 sm:mx-5" id="list-rows">
      <ListRow 
        v-for="row in rows" 
        :key="row.full_name" 
        v-slot="{ idx, column, item }"
        :row="row"
      >
        <ListRowItem :item="item">
          <template #default="{ label }">
            <div class="truncate text-base">
              {{ label }}
            </div>
          </template>
        </ListRowItem>
      </ListRow>
    </ListRows>
  </ListView>
</template>

<script setup>
import { ListView, ListRows, ListRow, ListRowItem } from 'frappe-ui'
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  rows: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['showScheduledCall'])
</script>