<template>
    <ListView
      :columns="columns"
      :rows="rows"
      :options="{
        onRowClick: (row) => emit('showScheduledCall', row),
        selectable: options.selectable,
        showTooltip: options.showTooltip,
        resizeColumn: options.resizeColumn,
      }"
      row-key="name"
      v-bind="$attrs"
    >
      <ListRows class="mx-3 sm:mx-5" id="list-rows">
        <ListRow
          v-for="row in rows"
          :key="row.name"
          v-slot="{ idx, column, item }"
          :row="row"
        >
          <ListRowItem :item="item">
            <template #default="{ label }">
              <div v-if="column.key === 'custom_first_date'">
                {{ item.custom_first_date }}
              </div>
              <div v-else-if="column.key === 'actions'">
                <slot name="actions" :row="row">
                  <div>No actions defined</div>
                </slot>
              </div>
              <div v-else>
                {{ label }}
              </div>
            </template>
          </ListRowItem>
        </ListRow>
      </ListRows>
    </ListView>
  </template>
  
  <script setup>
  import { defineProps, defineEmits } from 'vue'
  import { ListView, ListRows, ListRow, ListRowItem } from 'frappe-ui'
  
  const props = defineProps({
    columns: {
      type: Array,
      required: true
    },
    rows: {
      type: Array,
      default: () => []
    },
    options: {
      type: Object,
      default: () => ({
        selectable: false,
        showTooltip: false,
        resizeColumn: false
      })
    }
  })
  
  const emit = defineEmits(['showScheduledCall', 'loadMore'])
  </script>