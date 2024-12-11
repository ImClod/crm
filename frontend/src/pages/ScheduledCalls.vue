<template>
  <div>
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Scheduled Calls" />
      </template>
      <template #right-header>
        <CustomActions v-if="scheduledCallsListView?.customListActions"
          :actions="scheduledCallsListView.customListActions" />
      </template>
    </LayoutHeader>

    <ViewControls ref="viewControls" v-model="scheduledCalls" v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize" v-model:updatedPageCount="updatedPageCount" doctype="CRM Scheduled Call" />

      <ScheduledCallsListView 
        :rows="rows" 
        :columns="columns"
      />
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
  url: 'crm.api.contact.get_scheduled_calls',
  auto: true,
  transform(data) {
    console.log("API Response:", data); // Debugging statement
    return data.map(call => ({
      ...call,
      full_name: call.full_name || 'Unknown',
      status: call.custom_first_date || 'Pending'
    }))
  }
})

const rows = computed(() => {
  // Controlla se scheduledCalls.value e scheduledCalls.value.data esistono
  if (!scheduledCalls.value?.data) return []

  // Mappa i dati direttamente dall'array
  return scheduledCalls.value.data.map(item => ({
    full_name: item.full_name,
    email: item.email,
    mobile_no: item.mobile_no,
    status: item.status || item.custom_first_date
  }))
})

const columns = computed(() => [
  { 
    label: 'Nome', 
    key: 'full_name', 
    type: 'Data',
    width: '200px'
  },
  { 
    label: 'Email', 
    key: 'email', 
    type: 'Data',
    width: '250px'
  },
  { 
    label: 'Numero Mobile', 
    key: 'mobile_no', 
    type: 'Data',
    width: '150px'
  },
  { 
    label: 'Stato', 
    key: 'status', 
    type: 'Data',
    width: '150px'
  }
])
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