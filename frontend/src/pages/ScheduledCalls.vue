<template>
  <div>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs 
          v-model="viewControls" 
          routeName="Scheduled Calls" 
        />
      </template>
      <template #right-header>
        <CustomActions
          v-if="scheduledCallsListView?.customListActions"
          :actions="scheduledCallsListView.customListActions"
        />
      </template>
    </LayoutHeader>

    <ViewControls
      ref="viewControls"
      v-model="scheduledCalls"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      doctype="CRM Scheduled Call"
    />

    <ScheduledCallsListView
      ref="scheduledCallsListView"
      v-if="scheduledCalls.data && rows.length"
      v-model="scheduledCalls.data.page_length_count"
      v-model:list="scheduledCalls"
      :rows="rows"
      :columns="scheduledCalls.data.columns"
      :options="{
        showTooltip: false,
        resizeColumn: true,
        rowCount: scheduledCalls.data.row_count,
        totalCount: scheduledCalls.data.total_count,
      }"
      @showScheduledCall="showScheduledCall"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
      @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
      @likeDoc="(data) => viewControls.likeDoc(data)"
    />

    <div 
      v-else-if="scheduledCalls.data"
      class="flex h-full items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <PhoneIcon class="h-10 w-10" />
        <span>{{ __('No {0} Found', [__('Scheduled Calls')]) }}</span>
      </div>
    </div>

    <ScheduledCallModal 
      v-model="showScheduledCallModal" 
      :call="selectedScheduledCall" 
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'

import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import ScheduledCallsListView from '@/components/ListViews/ScheduledCallsListView.vue'
import ScheduledCallModal from '@/components/Modals/ScheduledCallModal.vue'

const scheduledCallsListView = ref(null)
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const scheduledCalls = createResource({
  url: 'crm.api.contacts.get_scheduled_calls',
  auto: true,
  transform(data) {
    console.log("API Response:", data); // Debugging statement
    return data.map(call => ({
      ...call,
      full_name: call.full_name || 'Unknown',
      status: call.status || 'Pending'
    }))
  }
})

const rows = computed(() => {
  if (
    !scheduledCalls.value?.data?.data ||
    !['list', 'group_by'].includes(scheduledCalls.value.data.view_type)
  )
    return []

  return scheduledCalls.value?.data.data.map((scheduledCall) => {
    let _rows = {}
    scheduledCalls.value?.data.rows.forEach((row) => {
      _rows[row] = scheduledCall[row]
    })
    return _rows
  })
})

// Watch for changes in scheduledCalls to log the transformed data
watch(scheduledCalls, (newValue) => {
  console.log("Transformed Data:", newValue); // Debugging statement
})

const showScheduledCallModal = ref(false)
const selectedScheduledCall = ref(null)

function showScheduledCall(call) {
  selectedScheduledCall.value = call
  showScheduledCallModal.value = true
}
</script>